"""
WebPilot 国内平台适配器示例

展示如何使用国内平台适配器简化微信、抖音、小红书、B站等平台的自动化操作。
"""

import asyncio
from webpilot import Browser
from webpilot.adapters import (
    WechatAdapter,
    DouyinAdapter,
    XiaohongshuAdapter,
    BilibiliAdapter,
)


async def wechat_example():
    """微信自动化示例"""
    browser = await Browser.launch(headless=False)

    try:
        page = await browser.new_page()
        wechat = WechatAdapter(page)

        # 获取登录二维码
        await wechat.login()
        qrcode = await wechat.get_qrcode("wechat_qrcode.png")
        print("请扫描 wechat_qrcode.png 中的二维码登录")

        # 等待登录
        import asyncio
        for _ in range(60):
            if await wechat.is_logged_in():
                print("登录成功!")
                break
            await asyncio.sleep(1)

        # 获取联系人列表
        contacts = await wechat.get_contacts()
        print(f"共有 {len(contacts)} 个联系人")

    finally:
        await browser.close()


async def douyin_example():
    """抖音自动化示例"""
    browser = await Browser.launch(headless=True)

    try:
        page = await browser.new_page()
        douyin = DouyinAdapter(page)

        # 搜索视频
        videos = await douyin.search("Python教程")
        print(f"找到 {len(videos)} 个视频:")
        for i, video in enumerate(videos[:5]):
            print(f"{i+1}. {video['title']} - {video['author']}")

        # 滚动推荐流
        await page.goto("https://www.douyin.com")
        await douyin.scroll_feed(3)

    finally:
        await browser.close()


async def xiaohongshu_example():
    """小红书自动化示例"""
    browser = await Browser.launch(headless=True)

    try:
        page = await browser.new_page()
        xhs = XiaohongshuAdapter(page)

        # 搜索笔记
        notes = await xhs.search("旅行攻略")
        print(f"找到 {len(notes)} 篇笔记:")
        for i, note in enumerate(notes[:5]):
            print(f"{i+1}. {note['title']} - {note['author']}")

    finally:
        await browser.close()


async def bilibili_example():
    """B站自动化示例"""
    browser = await Browser.launch(headless=True)

    try:
        page = await browser.new_page()
        bili = BilibiliAdapter(page)

        # 搜索视频
        videos = await bili.search_video("Python爬虫")
        print(f"找到 {len(videos)} 个视频:")
        for i, video in enumerate(videos[:5]):
            print(f"{i+1}. {video['title']} - {video['author']}")

        # 获取视频详情
        info = await bili.get_video_info("BV1xx411c7mD")
        print(f"视频标题: {info['title']}")
        print(f"视频描述: {info['description']}")

    finally:
        await browser.close()


if __name__ == "__main__":
    print("=== 抖音示例 ===")
    asyncio.run(douyin_example())

    print("\n=== 小红书示例 ===")
    asyncio.run(xiaohongshu_example())

    print("\n=== B站示例 ===")
    asyncio.run(bilibili_example())

    print("\n=== 微信示例 (需要扫码) ===")
    # asyncio.run(wechat_example())  # 取消注释以运行
