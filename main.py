from playwright.sync_api import sync_playwright
import time

def log(msg):
    print(msg, flush=True)

def run():
    with sync_playwright() as p:
        log("启动浏览器")

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        log("正在打开 Aternos")
        page.goto("https://aternos.org/go/")

        page.wait_for_load_state("domcontentloaded")
        log("基础加载完成")

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