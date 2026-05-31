import time
import traceback
from playwright.sync_api import sync_playwright

def log(msg):
    print(f"[LOG] {msg}", flush=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        page = browser.new_page()

        log("启动成功，进入主循环")

        while True:
            try:
                log("访问页面...")
                page.goto("https://aternos.org", wait_until="domcontentloaded")

                title = page.title()
                log(f"页面标题: {title}")

                # 示例：每 60 秒执行一次
                time.sleep(60)

            except Exception as e:
                log("发生错误：")
                log(traceback.format_exc())

                # 出错后短暂等待继续
                time.sleep(10)

def main():
    while True:
        try:
            run()
        except Exception:
            log("浏览器崩溃，重启中...")
            log(traceback.format_exc())
            time.sleep(5)

if __name__ == "__main__":
    main()