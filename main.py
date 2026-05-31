from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import subprocess
import time
import threading
import os
import glob
from http.server import HTTPServer, BaseHTTPRequestHandler

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

def find_camoufox_binary():
    patterns = [
        "/root/.cache/camoufox/**/camoufox",
        "/root/.cache/camoufox/**/firefox",
        os.path.expanduser("~/.cache/camoufox/**/camoufox"),
        os.path.expanduser("~/.cache/camoufox/**/firefox"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if os.path.isfile(match) and os.access(match, os.X_OK):
                log(f"找到 camoufox 二进制: {match}")
                return match
    log("未找到 camoufox 二进制，列出缓存目录:")
    try:
        result = subprocess.run(
            ["find", "/root/.cache/camoufox", "-type", "f"],
            capture_output=True, text=True, timeout=5
        )
        log(result.stdout[:500])
    except Exception as e:
        log(f"列目录失败: {e}")
    return None

def run():
    with sync_playwright() as p:
        camoufox_bin = find_camoufox_binary()

        if camoufox_bin:
            log(f"使用 camoufox Firefox: {camoufox_bin}")
            browser = p.firefox.launch(
                executable_path=camoufox_bin,
                headless=False,
            )
        else:
            log("camoufox 未找到，使用普通 Firefox")
            browser = p.firefox.launch(headless=True)

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
                "Gecko/20100101 Firefox/125.0"
            ),
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        page = context.new_page()
        stealth_sync(page)

        log("打开 https://aternos.org/go/")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded", timeout=60000)

        while True:
            url = page.url
            title = page.title()
            log(f"网址: {url} | 标题: {title}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    start_xvfb()
    while True:
        try:
            run()
        except Exception as e:
            log(f"错误，重启: {e}")
            time.sleep(5)