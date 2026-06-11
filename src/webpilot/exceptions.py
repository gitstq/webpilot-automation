"""
WebPilot 异常类定义

定义了所有WebPilot相关的异常类型，便于用户进行精确的错误处理。
"""


class WebPilotError(Exception):
    """WebPilot基础异常类"""

    def __init__(self, message: str = "", *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class BrowserError(WebPilotError):
    """浏览器相关错误"""
    pass


class PageError(WebPilotError):
    """页面相关错误"""
    pass


class ElementNotFoundError(PageError):
    """元素未找到错误"""
    pass


class NavigationError(PageError):
    """页面导航错误"""
    pass


class TimeoutError(WebPilotError):
    """操作超时错误"""
    pass


class CDPError(WebPilotError):
    """Chrome DevTools Protocol 通信错误"""
    pass


class AntiDetectError(WebPilotError):
    """反检测配置错误"""
    pass


class AIAgentError(WebPilotError):
    """AI Agent 相关错误"""
    pass


class RecordingError(WebPilotError):
    """录制回放相关错误"""
    pass
