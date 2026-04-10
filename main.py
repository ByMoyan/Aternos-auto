from playwright.sync_api import sync_playwright
import time
import datetime

def log(step, msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{step}] {msg}", flush=True)

def run():
    with sync_playwright() as p:
        log("系统", "启动浏览器")

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        log("页面", "正在打开 Aternos")
        page.goto("https://aternos.org/go/")

        page.wait_for_load_state("domcontentloaded")
        log("页面", "基础加载完成")

        while True:
            try:
                url = page.url
                title = page.title()

                log("状态", f"当前网址: {url}")
                log("状态", f"页面标题: {title}")

                if page.locator("text=Login").count() > 0:
                    log("检测", "找到 Login 按钮")
                else:
                    log("检测", "未找到 Login 按钮")

            except Exception as e:
                log("错误", str(e))

            time.sleep(20)

if __name__ == "__main__":
    run()