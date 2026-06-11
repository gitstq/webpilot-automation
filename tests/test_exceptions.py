"""
异常类测试
"""

import pytest
from webpilot.exceptions import (
    WebPilotError,
    BrowserError,
    PageError,
    ElementNotFoundError,
    NavigationError,
    TimeoutError,
    CDPError,
)


class TestExceptions:
    """测试异常类"""

    def test_webpilot_error(self):
        """测试基础异常"""
        error = WebPilotError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"

    def test_browser_error(self):
        """测试浏览器错误"""
        error = BrowserError("浏览器启动失败")
        assert isinstance(error, WebPilotError)
        assert str(error) == "浏览器启动失败"

    def test_page_error(self):
        """测试页面错误"""
        error = PageError("页面操作失败")
        assert isinstance(error, WebPilotError)
        assert str(error) == "页面操作失败"

    def test_element_not_found_error(self):
        """测试元素未找到错误"""
        error = ElementNotFoundError("未找到元素 #test")
        assert isinstance(error, PageError)
        assert str(error) == "未找到元素 #test"

    def test_navigation_error(self):
        """测试导航错误"""
        error = NavigationError("导航超时")
        assert isinstance(error, PageError)
        assert str(error) == "导航超时"

    def test_timeout_error(self):
        """测试超时错误"""
        error = TimeoutError("操作超时")
        assert isinstance(error, WebPilotError)
        assert str(error) == "操作超时"

    def test_cdp_error(self):
        """测试CDP错误"""
        error = CDPError("CDP通信失败")
        assert isinstance(error, WebPilotError)
        assert str(error) == "CDP通信失败"
