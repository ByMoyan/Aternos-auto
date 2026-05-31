from camoufox.sync_api import Camoufox as Firefox
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

def log(msg):
    print(msg, flush=True)

CLOUDFLARE_TITLES = ["just a moment", "请稍候", "一下"]

def is_cloudflare_page(title, url):
    title_lower = title.lower()
    for cf_title in CLOUDFLARE_TITLES:
        if cf_title in title_lower:
            return True
    if "challenge" in url.lower() or "/cdn-cgi/" in url.lower():
        return True
    return False

def wait_for_cloudflare(page, timeout=120):
    log("等待 Cloudflare 验证通过...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            title = page.title()
            url = page.url
            if not is_cloudflare_page(title, url):
                log(f"Cloudflare 已通过，当前页面: {title}")
                return True
            log(f"仍在验证中: {title}")
        except Exception:
            pass
        time.sleep(3)
    log("警告: Cloudflare 验证超时")
    return False

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    log(f"Health server 启动在端口 {port}")
    server.serve_forever()

def run():
    log("启动浏览器 (camoufox/Firefox)")
    with Firefox(headless=True) as browser:
        page = browser.new_page()
        log("正在打开 Aternos")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")
        wait_for_cloudflare(page, timeout=120)
        while True:
            try:
                url = page.url
                title = page.title()
                log(f"当前网址: {url}")
                log(f"页面标题: {title}")
            except Exception as e:
                log(f"错误: {e}")
            time.sleep(20)

if __name__ == "__main__":
    t = threading