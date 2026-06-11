"""
录制回放模块

提供用户操作录制和回放功能，类似Playwright的codegen。
支持生成Python代码、JSON脚本等多种输出格式。
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .exceptions import RecordingError


class ActionType(Enum):
    """操作类型"""
    GOTO = "goto"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    HOVER = "hover"
    PRESS = "press"


@dataclass
class RecordedAction:
    """录制的操作"""
    action_type: ActionType
    timestamp: float
    selector: Optional[str] = None
    value: Optional[str] = None
    position: Optional[dict[str, float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action_type.value,
            "timestamp": self.timestamp,
            "selector": self.selector,
            "value": self.value,
            "position": self.position,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecordedAction":
        return cls(
            action_type=ActionType(data["action"]),
            timestamp=data["timestamp"],
            selector=data.get("selector"),
            value=data.get("value"),
            position=data.get("position"),
            metadata=data.get("metadata", {}),
        )


class Recorder:
    """操作录制器"""

    def __init__(self) -> None:
        self._actions: list[RecordedAction] = []
        self._recording = False
        self._start_time: float = 0

    def start(self) -> None:
        """开始录制"""
        self._actions = []
        self._recording = True
        self._start_time = time.time()

    def stop(self) -> list[RecordedAction]:
        """停止录制并返回操作列表"""
        self._recording = False
        return self._actions.copy()

    def record(
        self,
        action_type: ActionType,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        position: Optional[dict[str, float]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """记录一个操作"""
        if not self._recording:
            return

        action = RecordedAction(
            action_type=action_type,
            timestamp=time.time() - self._start_time,
            selector=selector,
            value=value,
            position=position,
            metadata=metadata or {},
        )
        self._actions.append(action)

    def record_goto(self, url: str) -> None:
        """记录导航操作"""
        self.record(ActionType.GOTO, value=url)

    def record_click(self, selector: str, position: Optional[dict[str, float]] = None) -> None:
        """记录点击操作"""
        self.record(ActionType.CLICK, selector=selector, position=position)

    def record_type(self, selector: str, text: str) -> None:
        """记录输入操作"""
        self.record(ActionType.TYPE, selector=selector, value=text)

    def record_select(self, selector: str, value: str) -> None:
        """记录选择操作"""
        self.record(ActionType.SELECT, selector=selector, value=value)

    def record_scroll(self, x: float, y: float) -> None:
        """记录滚动操作"""
        self.record(ActionType.SCROLL, position={"x": x, "y": y})

    def record_wait(self, duration: float) -> None:
        """记录等待操作"""
        self.record(ActionType.WAIT, value=str(duration))

    def record_screenshot(self, path: Optional[str] = None) -> None:
        """记录截图操作"""
        self.record(ActionType.SCREENSHOT, value=path)

    def record_hover(self, selector: str) -> None:
        """记录悬停操作"""
        self.record(ActionType.HOVER, selector=selector)

    def record_press(self, key: str) -> None:
        """记录按键操作"""
        self.record(ActionType.PRESS, value=key)

    def to_json(self) -> str:
        """导出为JSON"""
        data = {
            "version": "1.0",
            "created_at": time.time(),
            "actions": [action.to_dict() for action in self._actions],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def to_python_code(self, use_async: bool = True) -> str:
        """导出为Python代码"""
        lines = [
            "import asyncio",
            "from webpilot import Browser",
            "",
        ]

        if use_async:
            lines.extend([
                "async def main():",
                '    browser = await Browser.launch(headless=False)',
                '    page = await browser.new_page()',
                "",
            ])
        else:
            lines.extend([
                "def main():",
                '    browser = Browser.launch_sync(headless=False)',
                '    page = browser.new_page()',
                "",
            ])

        indent = "    "

        for action in self._actions:
            if action.action_type == ActionType.GOTO:
                lines.append(f'{indent}await page.goto("{action.value}")' if use_async else f'{indent}page.goto("{action.value}")')
            elif action.action_type == ActionType.CLICK:
                lines.append(f'{indent}await page.click("{action.selector}")' if use_async else f'{indent}page.click("{action.selector}")')
            elif action.action_type == ActionType.TYPE:
                lines.append(f'{indent}await page.type("{action.selector}", "{action.value}")' if use_async else f'{indent}page.type("{action.selector}", "{action.value}")')
            elif action.action_type == ActionType.SELECT:
                lines.append(f'{indent}element = await page.query_selector("{action.selector}")' if use_async else f'{indent}element = page.query_selector("{action.selector}")')
                lines.append(f'{indent}await element.select_option("{action.value}")' if use_async else f'{indent}element.select_option("{action.value}")')
            elif action.action_type == ActionType.SCROLL:
                x = action.position.get("x", 0) if action.position else 0
                y = action.position.get("y", 0) if action.position else 0
                lines.append(f'{indent}await page.evaluate("window.scrollTo({x}, {y})")' if use_async else f'{indent}page.evaluate("window.scrollTo({x}, {y})")')
            elif action.action_type == ActionType.WAIT:
                lines.append(f'{indent}await asyncio.sleep({action.value})' if use_async else f'{indent}time.sleep({action.value})')
            elif action.action_type == ActionType.SCREENSHOT:
                path = action.value or "screenshot.png"
                lines.append(f'{indent}await page.screenshot("{path}")' if use_async else f'{indent}page.screenshot("{path}")')
            elif action.action_type == ActionType.HOVER:
                lines.append(f'{indent}element = await page.query_selector("{action.selector}")' if use_async else f'{indent}element = page.query_selector("{action.selector}")')
                lines.append(f'{indent}await element.hover()' if use_async else f'{indent}element.hover()')
            elif action.action_type == ActionType.PRESS:
                lines.append(f'{indent}# 按键: {action.value}')

        lines.extend([
            "",
            f'{indent}await browser.close()' if use_async else f'{indent}browser.close()',
            "",
        ])

        if use_async:
            lines.extend([
                'if __name__ == "__main__":',
                '    asyncio.run(main())',
            ])
        else:
            lines.extend([
                'if __name__ == "__main__":',
                '    main()',
            ])

        return "\n".join(lines)

    def save(self, path: str, format: str = "json") -> None:
        """
        保存录制内容

        Args:
            path: 保存路径
            format: 格式 (json/python)
        """
        if format == "json":
            content = self.to_json()
        elif format == "python":
            content = self.to_python_code()
        else:
            raise RecordingError(f"不支持的格式: {format}")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    @classmethod
    def load(cls, path: str) -> "Recorder":
        """从JSON文件加载录制内容"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        recorder = cls()
        for action_data in data.get("actions", []):
            action = RecordedAction.from_dict(action_data)
            recorder._actions.append(action)

        return recorder


class Player:
    """操作播放器"""

    def __init__(self, page: Any) -> None:
        self._page = page

    async def play(
        self,
        actions: list[RecordedAction],
        speed: float = 1.0,
    ) -> None:
        """
        播放录制的操作

        Args:
            actions: 操作列表
            speed: 播放速度倍数
        """
        last_timestamp = 0

        for action in actions:
            # 等待时间间隔
            wait_time = (action.timestamp - last_timestamp) / speed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            last_timestamp = action.timestamp

            # 执行操作
            await self._execute_action(action)

    async def _execute_action(self, action: RecordedAction) -> None:
        """执行单个操作"""
        from .page import Page

        page: Page = self._page

        if action.action_type == ActionType.GOTO:
            await page.goto(action.value or "")
        elif action.action_type == ActionType.CLICK:
            if action.selector:
                await page.click(action.selector)
        elif action.action_type == ActionType.TYPE:
            if action.selector and action.value:
                await page.type(action.selector, action.value)
        elif action.action_type == ActionType.SELECT:
            if action.selector and action.value:
                element = await page.query_selector(action.selector)
                if element:
                    await element.select_option(action.value)
        elif action.action_type == ActionType.SCROLL:
            if action.position:
                x = action.position.get("x", 0)
                y = action.position.get("y", 0)
                await page.evaluate(f"window.scrollTo({x}, {y})")
        elif action.action_type == ActionType.WAIT:
            if action.value:
                await asyncio.sleep(float(action.value))
        elif action.action_type == ActionType.SCREENSHOT:
            await page.screenshot(action.value)
        elif action.action_type == ActionType.HOVER:
            if action.selector:
                element = await page.query_selector(action.selector)
                if element:
                    await element.hover()
        elif action.action_type == ActionType.PRESS:
            # 按键操作需要特殊处理
            pass
