from camoufox.sync_api import Camoufox as Firefox
import subprocess
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

os.environ["CAMOUFOX_UPDATE"] = "0"
os.environ["CAMOUFOX_SKIP_UPDATE"] = "1"

def log(msg):
    print(msg, flush=True)

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
        time.sleep(2)
        log("Xvfb 已启动")
    except Exception as e:
        log(f"Xvfb 启动失败: {e}")

CLOUDFLARE_TITLES = ["just a moment", "请稍候", "一下"]

def is_cloudflare_page(title, url):
    title_lower = title.lower()
    for cf_title in CLOUDFLARE_TITLES:
        if cf_title in title_lower:
            return True
    if "challenge" in url.lower() or "/cdn-cgi/" in url.lower():
        return True
    return False

def new_page_with_timeout(browser, timeout=30):
    result = {}
    def _create():
        try:
            result['page'] = browser.new_page()
        except Exception as e:
            result['error'] = e
    t = threading.Thread(target=_create)
    t.start()
    t.join(timeout=timeout)
    if 'page' in result:
        return result['page']
    elif 'error' in result:
        raise result['error']
    else:
        raise TimeoutError(f"new_page() 超时 ({timeout}秒)")

def run():
    log("启动 camoufox Firefox...")
    try:
        with Firefox(headless=True, geoip=False) as browser:
            log("Firefox 启动成功，新建页面...")
            page = new_page_with_timeout(browser, timeout=30)
            log("页面创建成功，打开 Aternos...")
            page.goto("https://aternos.org/go/", wait_until="domcontentloaded", timeout=60000)
            while True:
                url = page.url
                title = page.title()
                log(f"网址: {url} | 标题: {title}")
                if is_cloudflare_page(title, url):
                    log("仍在 Cloudflare 验证中，等待...")
                else:
                    log("已进入网站！")
                time.sleep(10)
    except Exception as e:
        log(f"错误: {e}")
        raise

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    start_xvfb()
    while True:
        try:
            run()
        except Exception as e:
            log(f"重启中: {e}")
            time.sleep(5)