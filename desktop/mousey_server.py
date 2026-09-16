#!/usr/bin/env python3
import json
import secrets
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pynput.mouse import Button, Controller

HOST = "0.0.0.0"
PORT = 8765
ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"
mouse = Controller()
PAIR_PIN = f"{secrets.randbelow(1_000_000):06d}"


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def _reply(self, status=200, body=None):
        raw = json.dumps(body or {"ok": True}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _page(self):
        path = WEB_ROOT / "index.html"
        if not path.exists():
            self.send_error(404, "Mousey web client not found")
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._page()
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path not in ("/", "/mouse"):
            self._reply(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._reply(400, {"error": "invalid json"})
            return

        if data.get("pin") != PAIR_PIN:
            self._reply(401, {"error": "invalid pin"})
            return

        action = data.get("action")
        try:
            if action == "move":
                dx = max(-100, min(100, float(data.get("dx", 0))))
                dy = max(-100, min(100, float(data.get("dy", 0))))
                mouse.move(dx, dy)
            elif action == "click":
                button = Button.left if data.get("button") == "left" else Button.right
                mouse.click(button)
            elif action == "down":
                button = Button.left if data.get("button") == "left" else Button.right
                mouse.press(button)
            elif action == "up":
                button = Button.left if data.get("button") == "left" else Button.right
                mouse.release(button)
            elif action == "scroll":
                mouse.scroll(0, max(-10, min(10, float(data.get("dy", 0)))))
            elif action == "ping":
                pass
            else:
                self._reply(400, {"error": "unknown action"})
                return
        except Exception as exc:
            self._reply(500, {"error": str(exc)})
            return

        self._reply()


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Mousey desktop receiver")
    print(f"Open on your iPhone: http://{local_ip()}:{PORT}")
    print(f"Pairing PIN: {PAIR_PIN}")
    print("Keep this terminal open. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mousey.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
