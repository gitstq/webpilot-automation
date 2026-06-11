"""
元素操作模块

提供对网页元素的各种操作：点击、输入、获取属性、截图等。
支持链式调用和智能等待。
"""

import asyncio
from typing import Any, Optional

from .cdp_client import CDPClient
from .exceptions import ElementNotFoundError, PageError


class Element:
    """页面元素"""

    def __init__(
        self,
        cdp_client: CDPClient,
        session_id: str,
        remote_object: dict[str, Any],
    ) -> None:
        self._cdp = cdp_client
        self._session_id = session_id
        self._remote_object = remote_object
        self._object_id = remote_object.get("objectId")

    async def click(self) -> None:
        """点击元素"""
        # 获取元素位置
        box = await self.bounding_box()
        if not box:
            raise ElementNotFoundError("无法获取元素位置")

        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2

        # 模拟鼠标点击
        await self._cdp.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": center_x,
                "y": center_y,
                "button": "left",
                "clickCount": 1,
            },
            session_id=self._session_id,
        )

        await asyncio.sleep(0.05)

        await self._cdp.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseReleased",
                "x": center_x,
                "y": center_y,
                "button": "left",
                "clickCount": 1,
            },
            session_id=self._session_id,
        )

    async def type(self, text: str, delay: float = 0.0) -> None:
        """
        在元素中输入文本

        Args:
            text: 输入文本
            delay: 每个字符之间的延迟(秒)
        """
        # 先聚焦元素
        await self.focus()

        for char in text:
            # 发送按键按下事件
            await self._cdp.send(
                "Input.dispatchKeyEvent",
                {
                    "type": "keyDown",
                    "text": char,
                },
                session_id=self._session_id,
            )

            # 发送按键释放事件
            await self._cdp.send(
                "Input.dispatchKeyEvent",
                {
                    "type": "keyUp",
                    "text": char,
                },
                session_id=self._session_id,
            )

            if delay > 0:
                await asyncio.sleep(delay)

    async def focus(self) -> None:
        """聚焦元素"""
        if not self._object_id:
            raise ElementNotFoundError("元素对象ID无效")

        await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": "function() { this.focus(); }",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

    async def text_content(self) -> str:
        """获取元素文本内容"""
        if not self._object_id:
            return ""

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": "function() { return this.textContent; }",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

        return result.get("result", {}).get("value", "")

    async def inner_html(self) -> str:
        """获取元素内部HTML"""
        if not self._object_id:
            return ""

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": "function() { return this.innerHTML; }",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

        return result.get("result", {}).get("value", "")

    async def get_attribute(self, name: str) -> Optional[str]:
        """
        获取元素属性

        Args:
            name: 属性名

        Returns:
            属性值或None
        """
        if not self._object_id:
            return None

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": f"function() {{ return this.getAttribute('{name}'); }}",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

        value = result.get("result", {}).get("value")
        return str(value) if value is not None else None

    async def set_attribute(self, name: str, value: str) -> None:
        """
        设置元素属性

        Args:
            name: 属性名
            value: 属性值
        """
        if not self._object_id:
            raise ElementNotFoundError("元素对象ID无效")

        await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": f"function() {{ this.setAttribute('{name}', '{value}'); }}",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

    async def bounding_box(self) -> dict[str, float]:
        """
        获取元素边界框

        Returns:
            包含x, y, width, height的字典
        """
        if not self._object_id:
            return {"x": 0, "y": 0, "width": 0, "height": 0}

        # 获取元素的位置和大小
        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": """
                    function() {
                        const rect = this.getBoundingClientRect();
                        return {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        };
                    }
                """,
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

        value = result.get("result", {}).get("value", {})
        return {
            "x": value.get("x", 0),
            "y": value.get("y", 0),
            "width": value.get("width", 0),
            "height": value.get("height", 0),
        }

    async def is_visible(self) -> bool:
        """检查元素是否可见"""
        if not self._object_id:
            return False

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": """
                    function() {
                        const style = window.getComputedStyle(this);
                        return style.display !== 'none' 
                            && style.visibility !== 'hidden' 
                            && style.opacity !== '0'
                            && this.offsetParent !== null;
                    }
                """,
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

        return result.get("result", {}).get("value", False)

    async def scroll_into_view(self) -> None:
        """滚动到元素位置"""
        if not self._object_id:
            raise ElementNotFoundError("元素对象ID无效")

        await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": "function() { this.scrollIntoView({ behavior: 'smooth', block: 'center' }); }",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

    async def hover(self) -> None:
        """鼠标悬停"""
        box = await self.bounding_box()
        if not box:
            raise ElementNotFoundError("无法获取元素位置")

        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2

        await self._cdp.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseMoved",
                "x": center_x,
                "y": center_y,
            },
            session_id=self._session_id,
        )

    async def select_option(self, value: str) -> None:
        """
        选择下拉框选项

        Args:
            value: 选项值
        """
        if not self._object_id:
            raise ElementNotFoundError("元素对象ID无效")

        await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": f"function() {{ this.value = '{value}'; this.dispatchEvent(new Event('change')); }}",
                "arguments": [],
                "returnByValue": True,
            },
            session_id=self._session_id,
        )

    async def query_selector(self, selector: str) -> Optional["Element"]:
        """
        在当前元素内查找子元素

        Args:
            selector: CSS选择器

        Returns:
            Element实例或None
        """
        if not self._object_id:
            return None

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": f"function() {{ return this.querySelector('{selector}'); }}",
                "arguments": [],
            },
            session_id=self._session_id,
        )

        remote_object = result.get("result", {})
        if remote_object.get("type") == "undefined" or remote_object.get("subtype") == "null":
            return None

        return Element(self._cdp, self._session_id, remote_object)

    async def query_selector_all(self, selector: str) -> list["Element"]:
        """
        在当前元素内查找所有匹配子元素

        Args:
            selector: CSS选择器

        Returns:
            Element列表
        """
        if not self._object_id:
            return []

        result = await self._cdp.send(
            "Runtime.callFunctionOn",
            {
                "objectId": self._object_id,
                "functionDeclaration": f"function() {{ return Array.from(this.querySelectorAll('{selector}')); }}",
                "arguments": [],
            },
            session_id=self._session_id,
        )

        remote_object = result.get("result", {})
        if remote_object.get("type") == "undefined" or remote_object.get("subtype") == "null":
            return []

        object_id = remote_object.get("objectId")
        if not object_id:
            return []

        properties = await self._cdp.send(
            "Runtime.getProperties",
            {
                "objectId": object_id,
                "ownProperties": True,
            },
            session_id=self._session_id,
        )

        elements = []
        for prop in properties.get("result", []):
            if prop.get("enumerable") and "value" in prop:
                value = prop["value"]
                if value.get("type") == "object" and value.get("subtype") == "node":
                    elements.append(Element(self._cdp, self._session_id, value))

        return elements

    def __repr__(self) -> str:
        return f"<Element objectId={self._object_id}>"
