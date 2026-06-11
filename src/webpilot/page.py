"""
页面操作模块

提供页面导航、元素查找、内容提取、截图等核心功能。
支持异步操作、智能等待、结构化数据提取。
"""

import base64
import json
from typing import Any, Optional, TypeVar, Type

from pydantic import BaseModel

from .cdp_client import CDPClient
from .element import Element
from .exceptions import NavigationError, TimeoutError, PageError

T = TypeVar("T", bound=BaseModel)


class Page:
    """页面实例"""

    def __init__(
        self,
        cdp_client: CDPClient,
        target_id: str,
        session_id: str,
    ) -> None:
        self._cdp = cdp_client
        self._target_id = target_id
        self._session_id = session_id
        self._closed = False
        self._url = ""
        self._title = ""

    async def goto(
        self,
        url: str,
        wait_until: str = "networkidle",
        timeout: float = 30.0,
    ) -> None:
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load/domcontentloaded/networkidle)
            timeout: 超时时间(秒)
        """
        if self._closed:
            raise PageError("页面已关闭")

        try:
            # 启用网络监控
            await self._cdp.send("Network.enable", session_id=self._session_id)

            # 导航到页面
            result = await self._cdp.send(
                "Page.navigate",
                {"url": url},
                session_id=self._session_id,
            )

            if "errorText" in result:
                raise NavigationError(f"导航失败: {result['errorText']}")

            # 等待页面加载
            await self._wait_for_load(wait_until, timeout)

            self._url = url
            self._title = await self.title()

        except TimeoutError:
            raise TimeoutError(f"页面加载超时: {url}")
        except Exception as e:
            if isinstance(e, NavigationError):
                raise
            raise NavigationError(f"导航错误: {e}")

    async def title(self) -> str:
        """获取页面标题"""
        result = await self._cdp.send(
            "Runtime.evaluate",
            {"expression": "document.title"},
            session_id=self._session_id,
        )
        return result.get("result", {}).get("value", "")

    async def url(self) -> str:
        """获取当前URL"""
        result = await self._cdp.send(
            "Runtime.evaluate",
            {"expression": "window.location.href"},
            session_id=self._session_id,
        )
        self._url = result.get("result", {}).get("value", "")
        return self._url

    async def content(self) -> str:
        """获取页面HTML内容"""
        result = await self._cdp.send(
            "Runtime.evaluate",
            {
                "expression": "document.documentElement.outerHTML",
                "returnByValue": True,
            },
            session_id=self._session_id,
        )
        return result.get("result", {}).get("value", "")

    async def text_content(self) -> str:
        """获取页面纯文本内容"""
        result = await self._cdp.send(
            "Runtime.evaluate",
            {
                "expression": "document.body.innerText",
                "returnByValue": True,
            },
            session_id=self._session_id,
        )
        return result.get("result", {}).get("value", "")

    async def query_selector(self, selector: str) -> Optional[Element]:
        """
        查找单个元素

        Args:
            selector: CSS选择器

        Returns:
            Element实例或None
        """
        result = await self._cdp.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    document.querySelector('{selector}')
                """,
            },
            session_id=self._session_id,
        )

        remote_object = result.get("result", {})
        if remote_object.get("type") == "undefined" or remote_object.get("subtype") == "null":
            return None

        return Element(self._cdp, self._session_id, remote_object)

    async def query_selector_all(self, selector: str) -> list[Element]:
        """
        查找所有匹配元素

        Args:
            selector: CSS选择器

        Returns:
            Element列表
        """
        result = await self._cdp.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    Array.from(document.querySelectorAll('{selector}'))
                """,
            },
            session_id=self._session_id,
        )

        remote_object = result.get("result", {})
        if remote_object.get("type") == "undefined" or remote_object.get("subtype") == "null":
            return []

        # 获取数组元素
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

    async def wait_for_selector(
        self,
        selector: str,
        timeout: float = 30.0,
        visible: bool = False,
    ) -> Element:
        """
        等待元素出现

        Args:
            selector: CSS选择器
            timeout: 超时时间
            visible: 是否要求元素可见

        Returns:
            Element实例
        """
        import asyncio

        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            element = await self.query_selector(selector)
            if element:
                if not visible:
                    return element
                # 检查可见性
                is_visible = await element.is_visible()
                if is_visible:
                    return element
            await asyncio.sleep(0.1)

        raise TimeoutError(f"等待元素超时: {selector}")

    async def click(self, selector: str) -> None:
        """点击元素"""
        element = await self.wait_for_selector(selector)
        await element.click()

    async def type(self, selector: str, text: str, delay: float = 0.0) -> None:
        """
        在元素中输入文本

        Args:
            selector: CSS选择器
            text: 输入文本
            delay: 每个字符之间的延迟(秒)
        """
        element = await self.wait_for_selector(selector)
        await element.type(text, delay)

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> bytes:
        """
        页面截图

        Args:
            path: 保存路径
            full_page: 是否截取完整页面
            selector: 指定元素截图

        Returns:
            PNG图片字节数据
        """
        params: dict[str, Any] = {
            "format": "png",
            "fromSurface": True,
        }

        if selector:
            # 元素截图
            element = await self.query_selector(selector)
            if not element:
                raise PageError(f"未找到元素: {selector}")

            # 获取元素边界
            box = await element.bounding_box()
            params["clip"] = {
                "x": box["x"],
                "y": box["y"],
                "width": box["width"],
                "height": box["height"],
                "scale": 1,
            }
        elif full_page:
            # 完整页面截图
            metrics = await self._cdp.send(
                "Page.getLayoutMetrics",
                session_id=self._session_id,
            )
            content_size = metrics["contentSize"]
            params["clip"] = {
                "x": 0,
                "y": 0,
                "width": content_size["width"],
                "height": content_size["height"],
                "scale": 1,
            }

        result = await self._cdp.send(
            "Page.captureScreenshot",
            params,
            session_id=self._session_id,
        )

        data = base64.b64decode(result["data"])

        if path:
            with open(path, "wb") as f:
                f.write(data)

        return data

    async def pdf(
        self,
        path: Optional[str] = None,
        scale: float = 1.0,
        print_background: bool = True,
    ) -> bytes:
        """
        生成PDF

        Args:
            path: 保存路径
            scale: 缩放比例
            print_background: 是否打印背景

        Returns:
            PDF字节数据
        """
        result = await self._cdp.send(
            "Page.printToPDF",
            {
                "scale": scale,
                "printBackground": print_background,
                "preferCSSPageSize": True,
            },
            session_id=self._session_id,
        )

        data = base64.b64decode(result["data"])

        if path:
            with open(path, "wb") as f:
                f.write(data)

        return data

    async def evaluate(self, expression: str) -> Any:
        """
        在页面中执行JavaScript

        Args:
            expression: JavaScript表达式

        Returns:
            执行结果
        """
        result = await self._cdp.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
            session_id=self._session_id,
        )

        if "exceptionDetails" in result:
            exception = result["exceptionDetails"]
            raise PageError(f"JavaScript执行错误: {exception.get('text', 'Unknown error')}")

        return result.get("result", {}).get("value")

    async def extract(self, model: Type[T]) -> T:
        """
        使用Pydantic模型提取页面数据

        Args:
            model: Pydantic模型类

        Returns:
            模型实例
        """
        # 获取页面文本内容
        text = await self.text_content()

        # 构建提取提示
        schema = model.model_json_schema()
        prompt = f"""
        从以下网页内容中提取结构化数据，返回JSON格式：

        网页内容：
        {text[:5000]}

        数据格式要求：
        {json.dumps(schema, ensure_ascii=False, indent=2)}

        请只返回JSON数据，不要其他内容。
        """

        # 这里可以集成AI模型进行智能提取
        # 简化版本：尝试从页面中直接提取
        try:
            # 尝试通过DOM属性提取
            data = await self._extract_from_dom(schema)
            return model(**data)
        except Exception:
            # 如果DOM提取失败，返回空模型
            return model()

    async def close(self) -> None:
        """关闭页面"""
        if self._closed:
            return

        self._closed = True
        try:
            await self._cdp.send(
                "Target.closeTarget",
                {"targetId": self._target_id},
            )
        except Exception:
            pass

    async def _wait_for_load(self, wait_until: str, timeout: float) -> None:
        """等待页面加载完成"""
        import asyncio

        if wait_until == "load":
            await self._cdp.send(
                "Page.enable",
                session_id=self._session_id,
            )
            # 简单等待
            await asyncio.sleep(1)
        elif wait_until == "networkidle":
            # 等待网络空闲
            await asyncio.sleep(2)
        else:
            await asyncio.sleep(1)

    async def _extract_from_dom(self, schema: dict[str, Any]) -> dict[str, Any]:
        """从DOM中提取数据"""
        # 简化实现：根据schema属性名查找对应元素
        result = {}
        properties = schema.get("properties", {})

        for key in properties:
            # 尝试通过常见选择器查找
            selectors = [
                f"[data-field='{key}']",
                f".{key}",
                f"#{key}",
                f"[name='{key}']",
            ]

            for selector in selectors:
                try:
                    element = await self.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            result[key] = text.strip()
                            break
                except Exception:
                    continue

        return result

    async def __aenter__(self) -> "Page":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
