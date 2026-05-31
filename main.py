from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time

def log(msg):
    print(msg, flush=True)

def wait_for_cloudflare(page, timeout=60):
    log("等待 Cloudflare 验证通过...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            title = page.title()
            url = page.url
            if "just a moment" not in title.lower() and "challenge" not in url.lower():
                log(f"Cloudflare 已通过，当前页面: {title}")
                return True
        except Exception:
            pass
        time.sleep(2)
    log("警告: Cloudflare 验证超时")
    return False

def run():
    with sync_playwright() as p:
        log("启动浏览器")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--start-maximized",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

        page = context.new_page()

        stealth_sync(page)

        log("正在打开 Aternos")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")

        wait_for_cloudflare(page, timeout=60)

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
    run()