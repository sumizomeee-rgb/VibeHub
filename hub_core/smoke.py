"""Live integration checks used by CI and the frozen executable's self-test."""
import time

import httpx


def exercise_server(base_url: str) -> dict:
    report = {"home": False, "tools": {}}
    with httpx.Client(base_url=base_url, trust_env=False, timeout=15) as client:
        home = client.get("/")
        home.raise_for_status()
        assert "<div id=\"root\"" in home.text
        report["home"] = True
        tools = client.get("/api/tools").json()
        assert tools
        for tool in tools:
            response = client.post(f"/api/tools/{tool['id']}/open", headers={"X-VibeHub-Request": "1"})
            assert response.status_code in {200, 202}, response.text
        # Wait until every route has been published before exercising Caddy.
        # Replacing its route table can reset an existing keep-alive connection,
        # so page checks must not overlap another tool's route publication.
        for tool in tools:
            deadline = time.monotonic() + 240
            while time.monotonic() < deadline:
                state = client.get(f"/api/tools/{tool['id']}").json()
                if state["status"] == "error":
                    raise AssertionError(f"{tool['id']}: {state['message']}")
                if state["status"] == "ready":
                    break
                time.sleep(0.25)
            else:
                raise AssertionError(f"Timeout: {tool['id']}")
            report["tools"][tool["id"]] = "ready"
        for tool in tools:
            page = client.get(tool["url"])
            page.raise_for_status()
            assert "text/html" in page.headers.get("content-type", "")
            assert client.get(tool["url"].rstrip("/"), follow_redirects=False).status_code == 308
        # Files that are separate from main.py must survive packaging and proxying.
        references = client.get("/tools/avatar_crop_tool/api/reference-images")
        references.raise_for_status()
        for reference in references.json():
            image = client.get("/tools/avatar_crop_tool/" + reference["url"])
            image.raise_for_status()
            assert image.content.startswith(b"\x89PNG")
        # Removed management endpoints must not accidentally serve the SPA.
        assert client.post("/api/build", headers={"X-VibeHub-Request": "1"}).status_code in {404, 405}
        assert client.get("/api/tools/avatar_crop_tool/code").status_code == 404
        assert client.get("/builder").status_code == 404
    return report
