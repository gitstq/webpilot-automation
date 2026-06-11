"""
B站适配器

提供哔哩哔哩(bilibili.com)的专用自动化API。
"""

from typing import Any

from ..page import Page


class BilibiliAdapter:
    """B站适配器"""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def search_video(self, keyword: str) -> list[dict[str, Any]]:
        """
        搜索视频

        Args:
            keyword: 搜索关键词

        Returns:
            视频列表
        """
        await self._page.goto(f"https://search.bilibili.com/all?keyword={keyword}")
        await self._page.wait_for_selector(".video-list-item", timeout=10)

        videos = []
        elements = await self._page.query_selector_all(".video-list-item")

        for element in elements[:10]:
            title_elem = await element.query_selector(".bili-video-card__info--tit")
            author_elem = await element.query_selector(".bili-video-card__info--author")

            videos.append({
                "title": await title_elem.text_content() if title_elem else "",
                "author": await author_elem.text_content() if author_elem else "",
            })

        return videos

    async def get_video_info(self, bvid: str) -> dict[str, Any]:
        """
        获取视频信息

        Args:
            bvid: 视频BV号

        Returns:
            视频信息
        """
        await self._page.goto(f"https://www.bilibili.com/video/{bvid}")
        await self._page.wait_for_selector(".video-info-title", timeout=10)

        title = await self._page.text_content(".video-info-title")
        description = await self._page.text_content(".desc-info-text")

        return {
            "title": title,
            "description": description,
            "bvid": bvid,
        }

    async def get_danmaku(self) -> list[str]:
        """
        获取弹幕列表

        Returns:
            弹幕列表
        """
        # 弹幕需要通过API获取，这里简化处理
        danmaku_elements = await self._page.query_selector_all(".bilibili-player-video-danmaku")
        danmaku = []

        for element in danmaku_elements[:50]:
            text = await element.text_content()
            if text:
                danmaku.append(text)

        return danmaku

    async def get_comments(self, max_count: int = 20) -> list[dict[str, Any]]:
        """
        获取视频评论

        Args:
            max_count: 最大评论数

        Returns:
            评论列表
        """
        comments = []
        elements = await self._page.query_selector_all(".reply-item")

        for element in elements[:max_count]:
            user_elem = await element.query_selector(".user-name")
            content_elem = await element.query_selector(".reply-content")

            if content_elem:
                comments.append({
                    "user": await user_elem.text_content() if user_elem else "",
                    "content": await content_elem.text_content(),
                })

        return comments
