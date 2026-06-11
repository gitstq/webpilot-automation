"""
抖音适配器

提供抖音网页版(douyin.com)的专用自动化API。
"""

from typing import Any, Optional

from ..page import Page


class DouyinAdapter:
    """抖音适配器"""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def search(self, keyword: str) -> list[dict[str, Any]]:
        """
        搜索视频

        Args:
            keyword: 搜索关键词

        Returns:
            视频列表
        """
        await self._page.goto(f"https://www.douyin.com/search/{keyword}")
        await self._page.wait_for_selector("[data-e2e='search-card-video']", timeout=10)

        videos = []
        elements = await self._page.query_selector_all("[data-e2e='search-card-video']")

        for element in elements[:10]:  # 只取前10个
            title_elem = await element.query_selector("[data-e2e='search-card-title']")
            author_elem = await element.query_selector("[data-e2e='search-card-user']")

            videos.append({
                "title": await title_elem.text_content() if title_elem else "",
                "author": await author_elem.text_content() if author_elem else "",
            })

        return videos

    async def get_video_info(self, video_url: str) -> dict[str, Any]:
        """
        获取视频信息

        Args:
            video_url: 视频链接

        Returns:
            视频信息
        """
        await self._page.goto(video_url)
        await self._page.wait_for_selector(".video-container", timeout=10)

        title = await self._page.evaluate("document.title")

        return {
            "title": title,
            "url": video_url,
        }

    async def get_comments(self, max_count: int = 20) -> list[dict[str, Any]]:
        """
        获取视频评论

        Args:
            max_count: 最大评论数

        Returns:
            评论列表
        """
        comments = []
        elements = await self._page.query_selector_all(".comment-item")

        for element in elements[:max_count]:
            user_elem = await element.query_selector(".user-name")
            content_elem = await element.query_selector(".comment-content")

            if content_elem:
                comments.append({
                    "user": await user_elem.text_content() if user_elem else "",
                    "content": await content_elem.text_content(),
                })

        return comments

    async def scroll_feed(self, count: int = 5) -> None:
        """
        滚动推荐流

        Args:
            count: 滚动次数
        """
        for _ in range(count):
            await self._page.evaluate("window.scrollBy(0, window.innerHeight)")
            import asyncio
            await asyncio.sleep(1)
