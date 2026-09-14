"""Exercise the unchanged tool applications, including Chinese download filenames."""
import base64
import importlib.util
import io
import unittest
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient
from hub_core.config import ROOT


class ExistingToolsTests(unittest.TestCase):
    def load_tool(self, name):
        path = ROOT / "projects" / name / "main.py"
        spec = importlib.util.spec_from_file_location(f"test_tool_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return TestClient(module.app)

    def test_all_homepages(self):
        from hub_core.catalog import Catalog
        for tool in Catalog(ROOT).tools:
            with self.subTest(tool=tool.id), self.load_tool(tool.id) as client:
                response = client.get("/")
                self.assertEqual(response.status_code, 200)
                self.assertIn("text/html", response.headers["content-type"])

    def test_avatar_assets(self):
        with self.load_tool("avatar_crop_tool") as client:
            references = client.get("/api/reference-images").json()
            self.assertGreater(len(references), 0)
            for reference in references:
                response = client.get("/" + reference["url"])
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.content.startswith(b"\x89PNG"))

    def test_images_to_pdf_upload_and_download(self):
        from PIL import Image
        image = io.BytesIO()
        Image.new("RGB", (16, 16), "white").save(image, "PNG")
        with self.load_tool("images_to_pdf_converter") as client:
            response = client.post("/api/convert", files={"images":("图片.png", image.getvalue(), "image/png")})
            self.assertEqual(response.status_code, 200)
            download = client.get("/api/download/" + response.json()["id"])
            self.assertEqual(download.status_code, 200)
            self.assertTrue(download.content.startswith(b"%PDF"))

    def test_chinese_pdf_to_png_and_zip(self):
        import fitz
        with fitz.open() as document:
            document.new_page(width=72, height=72)
            pdf = document.tobytes()
        with self.load_tool("pdf_to_images_converter") as client:
            converted = client.post("/convert", files={"file":("中文 文件.pdf", pdf, "application/pdf")})
            self.assertEqual(converted.status_code, 200)
            task = converted.json()["task_id"]
            self.assertTrue(client.get(f"/preview/{task}/1").content.startswith(b"\x89PNG"))
            download = client.get(f"/download/{task}")
            self.assertEqual(download.status_code, 200)
            self.assertIn("filename*=UTF-8''", download.headers["content-disposition"])
            self.assertEqual(int(download.headers["content-length"]), len(download.content))
            with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
                self.assertTrue(any("中文 文件" in name for name in archive.namelist()))

    def test_character_portrait_upload(self):
        from PIL import Image
        image = io.BytesIO()
        Image.new("RGBA", (32, 48), (255, 255, 255, 255)).save(image, "PNG")
        with self.load_tool("character_portrait_slicer") as client:
            response = client.post("/api/upload", files={"file":("立绘.png", image.getvalue(), "image/png")})
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__": unittest.main()
