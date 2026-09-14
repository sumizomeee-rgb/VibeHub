"""Real uv + Caddy + HTTP tests, optional browser UI checks, and shutdown checks."""
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import tempfile
import time
import zipfile

import httpx
import psutil

from hub_core.application import Application
from hub_core.config import Settings
from hub_core.smoke import exercise_server


def image_bytes() -> bytes:
    from PIL import Image
    result = io.BytesIO()
    Image.new("RGB", (32, 48), "white").save(result, "PNG")
    return result.getvalue()


def exercise_uploads(url: str):
    import fitz
    with httpx.Client(base_url=url, trust_env=False, timeout=30) as client:
        result = client.post("/tools/images_to_pdf_converter/api/convert", files={"images": ("图片.png", image_bytes(), "image/png")})
        result.raise_for_status()
        pdf = client.get(f"/tools/images_to_pdf_converter/api/download/{result.json()['id']}")
        pdf.raise_for_status()
        assert pdf.content.startswith(b"%PDF")
        converted = client.post("/tools/pdf_to_images_converter/convert", files={"file": ("中文 文件.pdf", pdf.content, "application/pdf")})
        converted.raise_for_status()
        task = converted.json()["task_id"]
        preview = client.get(f"/tools/pdf_to_images_converter/preview/{task}/1")
        assert preview.content.startswith(b"\x89PNG")
        download = client.get(f"/tools/pdf_to_images_converter/download/{task}")
        download.raise_for_status()
        assert "filename*=UTF-8''" in download.headers["content-disposition"]
        with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
            assert any("中文 文件" in name for name in archive.namelist())
        result = client.post("/tools/character_portrait_slicer/api/upload", files={"file": ("立绘.png", image_bytes(), "image/png")})
        result.raise_for_status()


def exercise_ui(url: str, output: Path, *, executable_path: str | None = None):
    from playwright.sync_api import sync_playwright, expect
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable_path)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 860}, accept_downloads=True)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(url)
            expect(page.locator("[data-tool-card]")).to_have_count(5)
            expect(page.get_by_text("新建工具", exact=True)).to_have_count(0)
            expect(page.get_by_text("管理", exact=True)).to_have_count(0)
            page.screenshot(path=str(output / "homepage.png"))
            page.locator('[data-tool-card="images_to_pdf_converter"]').click()
            frame = page.frame_locator('iframe[title="图片转 PDF"]')
            frame.locator('input[type="file"]').set_input_files({"name": "图片.png", "mimeType": "image/png", "buffer": image_bytes()})
            import base64
            frame.locator("#dropZone").evaluate("""(element, encoded) => {
              const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
              const transfer = new DataTransfer();
              transfer.items.add(new File([bytes], '拖拽图片.png', {type: 'image/png'}));
              element.dispatchEvent(new DragEvent('drop', {bubbles: true, dataTransfer: transfer}));
            }""", base64.b64encode(image_bytes()).decode())
            expect(frame.locator("#previewGrid .preview-item")).to_have_count(2)
            frame.locator("#convertBtn").click()
            expect(frame.locator("#downloadBtn")).to_be_visible()
            with page.expect_download() as download_info:
                frame.locator("#downloadBtn").click()
            download = download_info.value
            filename = output / "browser-download.pdf"
            download.save_as(filename)
            assert filename.read_bytes().startswith(b"%PDF")
            frame.locator("body").evaluate("element => { window.__vibehubStateCheck = 'preserved'; }")
            page.screenshot(path=str(output / "tool-workspace.png"))
            page.get_by_role("link", name="返回首页", exact=True).first.click()
            expect(page.locator("[data-tool-card]")).to_have_count(5)
            page.locator('[data-tool-card="images_to_pdf_converter"]').click()
            expect(frame.locator("#downloadBtn")).to_be_visible()
            assert frame.locator("body").evaluate("() => window.__vibehubStateCheck") == "preserved"
            # A desktop-sized narrow viewport still keeps the global home control visible.
            page.set_viewport_size({"width": 780, "height": 650})
            expect(page.get_by_role("link", name="返回首页", exact=True)).to_be_visible()
            assert not errors, errors
        finally:
            browser.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("verification"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pids = {}
    with tempfile.TemporaryDirectory(prefix="vibehub-check-") as directory:
        settings = replace(Settings.from_env(), data_dir=Path(directory), port=0)
        try:
            with Application(settings) as application:
                report = exercise_server(application.url)
                exercise_uploads(application.url)
                report["upload_download_proxy"] = "passed"
                if args.ui:
                    exercise_ui(application.url, args.output)
                    report["browser_ui_and_state"] = "passed"
                for child in psutil.Process().children(recursive=True):
                    pids[child.pid] = child.create_time()
            deadline = time.monotonic() + 6
            survivors = []
            while time.monotonic() < deadline:
                survivors = []
                for pid, created in pids.items():
                    try:
                        process = psutil.Process(pid)
                        if process.create_time() == created and process.status() != psutil.STATUS_ZOMBIE:
                            survivors.append(pid)
                    except psutil.NoSuchProcess:
                        pass
                if not survivors: break
                time.sleep(0.1)
            assert not survivors, f"Leaked child processes: {survivors}"
            report["shutdown_cleanup"] = "passed"
            (args.output / "integration.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            import shutil
            if (Path(directory) / "logs").exists():
                shutil.copytree(Path(directory) / "logs", args.output / "logs", dirs_exist_ok=True)


if __name__ == "__main__": main()
