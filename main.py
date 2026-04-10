from playwright.sync_api import sync_playwright
import time

def log(msg):
    print(msg, flush=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        log("打开 Aternos 页面")
        page.goto("https://aternos.org/go/")

        page.wait_for_load_state("networkidle")
        log("页面加载完成")

        while True:
            try:
                title = page.title()
                log(f"当前页面标题: {title}")

                url = page.url
                log(f"当前URL: {url}")

            except Exception as e:
                log(f"发生错误: {e}")

            time.sleep(30)

if __name__ == "__main__":
    run()