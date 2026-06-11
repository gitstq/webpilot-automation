"""
WebPilot - 新一代CDP浏览器自动化引擎

AI驱动、反检测增强、国内平台适配的浏览器自动化解决方案。
基于Chrome DevTools Protocol (CDP)，无需WebDriver即可实现强大的浏览器控制。

示例:
    >>> import asyncio
    >>> from webpilot import Browser, Page
    >>>
    >>> async def main():
    ...     browser = await Browser.launch()
    ...     page = await browser.new_page()
    ...     await page.goto("https://example.com")
    ...     title = await page.title()
    ...     print(title)
    ...     await browser.close()
    >>>
    >>> asyncio.run(main())
"""

__version__ = "1.0.0"
__author__ = "WebPilot Team"
__license__ = "MIT"

from .browser import Browser
from .page import Page
from .element import Element
from .exceptions import (
    WebPilotError,
    BrowserError,
    PageError,
    ElementNotFoundError,
    NavigationError,
    TimeoutError,
    CDPError,
)
from .anti_detect import AntiDetectConfig
from .ai_agent import AIAgent

__all__ = [
    "Browser",
    "Page",
    "Element",
    "WebPilotError",
    "BrowserError",
    "PageError",
    "ElementNotFoundError",
    "NavigationError",
    "TimeoutError",
    "CDPError",
    "AntiDetectConfig",
    "AIAgent",
]
