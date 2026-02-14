"""Lightweight Chrome DevTools Protocol client for script injection."""
import json
import urllib.request
import asyncio
from websockets.asyncio.client import connect as ws_connect


class CDPClient:
    """Short-lived CDP client for page discovery and script evaluation."""

    def __init__(self, port: int = 9222):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self._msg_id = 0

    def discover_pages(self) -> list[dict]:
        """GET /json to list all inspectable pages."""
        try:
            with urllib.request.urlopen(f"{self.base_url}/json", timeout=5) as resp:
                return json.loads(resp.read())
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to Chrome DevTools at {self.base_url}. "
                f"Ensure Chrome is running with --remote-debugging-port={self.port}"
            ) from e

    def evaluate(self, script: str, target_url: str | None = None) -> dict:
        """Discover page, connect via WS, run Runtime.evaluate, disconnect."""
        pages = self.discover_pages()
        page = self._find_target_page(pages, target_url)
        return asyncio.run(self._ws_evaluate(page["webSocketDebuggerUrl"], script))

    def _find_target_page(self, pages: list[dict], target_url: str | None) -> dict:
        """Select target page: match target_url or first suitable page."""
        suitable = [
            p for p in pages
            if p.get("type") == "page"
            and not p.get("url", "").startswith("chrome-extension://")
            and not p.get("url", "").startswith("devtools://")
        ]
        if not suitable:
            raise ValueError("No suitable browser page found")

        if target_url:
            for p in suitable:
                if target_url in p.get("url", ""):
                    return p
            raise ValueError(f"No page matching URL pattern: {target_url}")

        return suitable[0]

    async def _ws_evaluate(self, ws_url: str, expression: str) -> dict:
        """Connect via WebSocket, send Runtime.evaluate, return result."""
        self._msg_id += 1
        msg = {
            "id": self._msg_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        }
        async with ws_connect(ws_url) as ws:
            await ws.send(json.dumps(msg))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == self._msg_id:
                    return resp
