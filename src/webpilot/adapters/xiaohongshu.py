"""
小红书适配器

提供小红书(xiaohongshu.com)的专用自动化API。
"""

from typing import Any

from ..page import Page


class XiaohongshuAdapter:
    """小红书适配器"""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def search(self, keyword: str) -> list[dict[str, Any]]:
        """
        搜索笔记

        Args:
            keyword: 搜索关键词

        Returns:
            笔记列表
        """
        await self._page.goto(f"https://www.xiaohongshu.com/search_result?keyword={keyword}")
        await self._page.wait_for_selector(".note-item", timeout=10)

        notes = []
        elements = await self._page.query_selector_all(".note-item")

        for element in elements[:10]:
            title_elem = await element.query_selector(".title")
            author_elem = await element.query_selector(".author")

            notes.append({
                "title": await title_elem.text_content() if title_elem else "",
                "author": await author_elem.text_content() if author_elem else "",
            })

        return notes

    async def get_note_detail(self, note_url: str) -> dict[str, Any]:
        """
        获取笔记详情

        Args:
            note_url: 笔记链接

        Returns:
            笔记详情
        """
        await self._page.goto(note_url)
        await self._page.wait_for_selector(".note-content", timeout=10)

        title = await self._page.evaluate("document.title")
        content = await self._page.text_content(".note-content")

        return {
            "title": title,
            "content": content,
            "url": note_url,
        }

    async def get_comments(self, max_count: int = 20) -> list[dict[str, Any]]:
        """
        获取笔记评论

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
