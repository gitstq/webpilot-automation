"""
WebPilot 基础使用示例

展示WebPilot的核心功能：浏览器启动、页面导航、元素操作、截图等。
"""

import asyncio
from webpilot import Browser


async def basic_example():
    """基础示例"""
    # 启动浏览器
    browser = await Browser.launch(headless=True)

    try:
        # 创建新页面
        page = await browser.new_page()

        # 导航到网页
        await page.goto("https://example.com")

        # 获取页面标题
        title = await page.title()
        print(f"页面标题: {title}")

        # 获取页面内容
        content = await page.text_content()
        print(f"页面内容: {content[:200]}...")

        # 截图
        await page.screenshot("example.png")
        print("截图已保存: example.png")

    finally:
        # 关闭浏览器
        await browser.close()


async def element_interaction_example():
    """元素交互示例"""
    browser = await Browser.launch(headless=True)

    try:
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")

        # 输入搜索关键词
        await page.type("#kw", "WebPilot")

        # 点击搜索按钮
        await page.click("#su")

        # 等待结果加载
        await asyncio.sleep(2)

        # 获取搜索结果
        results = await page.query_selector_all(".result")
        print(f"找到 {len(results)} 个搜索结果")

        for i, result in enumerate(results[:3]):
            title = await result.query_selector("h3")
            if title:
                text = await title.text_content()
                print(f"结果 {i+1}: {text}")

    finally:
        await browser.close()


async def anti_detect_example():
    """反检测示例"""
    # 启用反检测模式
    browser = await Browser.launch(
        headless=True,
        anti_detect=True,
    )

    try:
        page = await browser.new_page()
        await page.goto("https://bot.sannysoft.com")

        # 截图查看检测结果
        await page.screenshot("bot_test.png")
        print("反检测测试截图已保存: bot_test.png")

    finally:
        await browser.close()


async def recorder_example():
    """录制回放示例"""
    from webpilot.recorder import Recorder

    browser = await Browser.launch(headless=True)
    recorder = Recorder()

    try:
        recorder.start()

        page = await browser.new_page()
        recorder.record_goto("https://example.com")
        await page.goto("https://example.com")

        recorder.record_click("a")
        await page.click("a")

        recorder.record_screenshot("recorded.png")
        await page.screenshot("recorded.png")

        # 停止录制并生成代码
        actions = recorder.stop()
        code = recorder.to_python_code()
        print("生成的代码:")
        print(code)

    finally:
        await browser.close()


if __name__ == "__main__":
    print("=== 基础示例 ===")
    asyncio.run(basic_example())

    print("\n=== 元素交互示例 ===")
    asyncio.run(element_interaction_example())

    print("\n=== 反检测示例 ===")
    asyncio.run(anti_detect_example())

    print("\n=== 录制回放示例 ===")
    asyncio.run(recorder_example())
