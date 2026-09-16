#!/usr/bin/env python3
import ctypes
import ipaddress
import json
import secrets
import socket
import ssl
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pynput.mouse import Button, Controller

HOST = "0.0.0.0"
PORT = 8765
ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"
CERT_DIR = Path(__file__).resolve().parent / ".mousey-cert"
CERT_FILE = CERT_DIR / "cert.pem"
KEY_FILE = CERT_DIR / "key.pem"
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

def screen_size():
    if hasattr(ctypes, "windll"):
        return ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    try:
        out = subprocess.check_output(["xrandr", "--current"], text=True, stderr=subprocess.DEVNULL)
        import re
        m = re.search(r"current\s+(\d+)\s+x\s+(\d+)", out)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    try:
        out = subprocess.check_output(["xdpyinfo"], text=True, stderr=subprocess.DEVNULL)
        import re
        m = re.search(r"dimensions:\s+(\d+)x(\d+)", out)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return None

def center_cursor():
    size = screen_size()
    if size:
        mouse.position = (size[0] // 2, size[1] // 2)

def ensure_certificate(ip):
    CERT_DIR.mkdir(exist_ok=True)
    try: ipaddress.ip_address(ip)
    except ValueError: ip = "127.0.0.1"
    cmd = ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes", "-days", "825", "-keyout", str(KEY_FILE), "-out", str(CERT_FILE), "-subj", "/CN=Mousey Local", "-addext", f"subjectAltName=IP:{ip},IP:127.0.0.1"]
    if not (CERT_FILE.exists() and KEY_FILE.exists()):
        try: subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (FileNotFoundError, subprocess.CalledProcessError) as exc: raise RuntimeError("OpenSSL is required. Install it with: sudo apt install openssl") from exc

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args): pass
    def _reply(self, status=200, body=None):
        raw = json.dumps(body or {"ok": True}).encode(); self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw))); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(raw)
    def _page(self):
        path = WEB_ROOT / "index.html"
        if not path.exists(): self.send_error(404, "Mousey web client not found"); return
        raw = path.read_bytes(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path in ("/", "/index.html"): self._page()
        else: self.send_error(404, "Not found")
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "Content-Type"); self.end_headers()
    def do_POST(self):
        if self.path not in ("/", "/mouse"): self._reply(404, {"error":"not found"}); return
        try:
            length = int(self.headers.get("Content-Length", "0")); data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError): self._reply(400, {"error":"invalid json"}); return
        if data.get("pin") != PAIR_PIN: self._reply(401, {"error":"invalid pin"}); return
        try:
            action = data.get("action")
            if action == "move": mouse.move(float(data.get("dx",0)), float(data.get("dy",0)))
            elif action == "center": center_cursor()
            elif action == "click": mouse.click(Button.left if data.get("button")=="left" else Button.right)
            elif action == "down": mouse.press(Button.left if data.get("button")=="left" else Button.right)
            elif action == "up": mouse.release(Button.left if data.get("button")=="left" else Button.right)
            elif action == "scroll": mouse.scroll(0, max(-10,min(10,float(data.get("dy",0)))))
            elif action == "ping": center_cursor()
            else: self._reply(400,{"error":"unknown action"}); return
        except Exception as exc: self._reply(500,{"error":str(exc)}); return
        self._reply()

def main():
    ip=local_ip(); ensure_certificate(ip); server=ThreadingHTTPServer((HOST,PORT),Handler); context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); context.load_cert_chain(certfile=CERT_FILE,keyfile=KEY_FILE); server.socket=context.wrap_socket(server.socket,server_side=True)
    print("Mousey desktop receiver"); print(f"Open on your iPhone: https://{ip}:{PORT}"); print(f"Pairing PIN: {PAIR_PIN}"); print("Keep this terminal open. Press Ctrl+C to stop.")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nStopping Mousey.")
    finally: server.server_close()
if __name__ == "__main__": main()
