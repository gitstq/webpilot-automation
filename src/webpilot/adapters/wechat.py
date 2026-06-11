"""
微信网页版适配器

提供微信网页版(wx.qq.com)的专用自动化API。
"""

from typing import Any, Optional

from ..page import Page


class WechatAdapter:
    """微信网页版适配器"""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def login(self) -> bool:
        """
        获取登录二维码并等待扫码登录

        Returns:
            是否登录成功
        """
        await self._page.goto("https://wx.qq.com")
        # 等待二维码加载
        try:
            await self._page.wait_for_selector(".qrcode", timeout=10)
            return True
        except Exception:
            return False

    async def get_qrcode(self, save_path: Optional[str] = None) -> bytes:
        """
        获取登录二维码图片

        Args:
            save_path: 保存路径

        Returns:
            二维码图片数据
        """
        return await self._page.screenshot(
            selector=".qrcode",
            path=save_path,
        )

    async def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            await self._page.wait_for_selector(".chat_list", timeout=5)
            return True
        except Exception:
            return False

    async def get_contacts(self) -> list[dict[str, Any]]:
        """
        获取联系人列表

        Returns:
            联系人列表
        """
        # 点击通讯录
        await self._page.click("#navContact")
        await self._page.wait_for_selector(".contact_item", timeout=10)

        contacts = []
        elements = await self._page.query_selector_all(".contact_item")
        for element in elements:
            name = await element.query_selector(".nickname")
            if name:
                contacts.append({
                    "name": await name.text_content(),
                })

        return contacts

    async def send_message(self, contact_name: str, message: str) -> bool:
        """
        发送消息给指定联系人

        Args:
            contact_name: 联系人名称
            message: 消息内容

        Returns:
            是否发送成功
        """
        try:
            # 搜索联系人
            await self._page.type("#search_contact", contact_name)
            await self._page.click(f"[title='{contact_name}']")

            # 输入消息
            await self._page.type("#editArea", message)

            # 发送
            await self._page.click(".btn_send")
            return True
        except Exception:
            return False

    async def get_messages(self) -> list[dict[str, Any]]:
        """
        获取当前聊天消息

        Returns:
            消息列表
        """
        messages = []
        elements = await self._page.query_selector_all(".message")

        for element in elements:
            content_elem = await element.query_selector(".content")
            sender_elem = await element.query_selector(".nickname")

            if content_elem:
                messages.append({
                    "sender": await sender_elem.text_content() if sender_elem else "",
                    "content": await content_elem.text_content(),
                })

        return messages
