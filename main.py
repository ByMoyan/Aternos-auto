from camoufox.sync_api import Camoufox as Firefox
import time
import threading
import subprocess
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

os.environ["CAMOUFOX_UPDATE"] = "0"
os.environ["CAMOUFOX_SKIP_UPDATE"] = "1"

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

def start_xvfb():
    try:
        subprocess.Popen(
            ["Xvfb", ":99", "-screen", "0", "1920x1080x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.environ["DISPLAY"] = ":99"
        time.sleep(1)
        log("Xvfb 已启动")
    except Exception as e:
        log(f"Xvfb 启动失败（继续尝试）: {e}")

def run():
    log("启动浏览器 (camoufox/Firefox)")
    try:
        with Firefox(headless=True, geoip=False) as browser:
            log("Firefox 启动完成，新建页面...")
            page = browser.new_page()
            log("正在打开 Aternos")
            page.goto("https://aternos.org/go/", wait_until="domcontentloaded", timeout=60000)
            wait_for_cloudflare(page, timeout=120)
            while True:
                try:
                    url = page.url
                    title = page.title()
                    log(f"当前网址: {url}")
                    log(f"页面标题: {title}")
                except Exception as e:
                    log(f"页面错误: {e}")
                time.sleep(20)
    except Exception as e:
        log(f"浏览器崩溃: {e}")
        raise

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()

    start_xvfb()

    while True:
        try:
            run()
        except Exception as e:
            log(f"重启浏览器，原因: {e}")
            time.sleep(5)