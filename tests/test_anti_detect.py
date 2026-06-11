"""
反检测模块测试
"""

import json
import pytest
from webpilot.anti_detect import AntiDetectConfig


class TestAntiDetectConfig:
    """测试反检测配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = AntiDetectConfig()
        assert config.screen_width == 1920
        assert config.screen_height == 1080
        assert config.timezone == "Asia/Shanghai"
        assert config.hardware_concurrency == 8
        assert config.device_memory == 8

    def test_custom_config(self):
        """测试自定义配置"""
        config = AntiDetectConfig(
            user_agent="Test Agent",
            screen_width=2560,
            screen_height=1440,
            timezone="America/New_York",
        )
        assert config.user_agent == "Test Agent"
        assert config.screen_width == 2560
        assert config.screen_height == 1440
        assert config.timezone == "America/New_York"

    def test_to_js_script(self):
        """测试生成JavaScript脚本"""
        config = AntiDetectConfig()
        script = config.to_js_script()
        assert isinstance(script, str)
        assert "navigator" in script
        assert "webdriver" in script
        assert "canvas" in script

    def test_random_config(self):
        """测试随机配置生成"""
        config = AntiDetectConfig.random()
        assert config.user_agent is not None
        assert config.platform in ["Win32", "MacIntel", "Linux x86_64"]

    def test_to_dict(self):
        """测试转换为字典"""
        config = AntiDetectConfig()
        data = config.to_dict()
        assert isinstance(data, dict)
        assert "screen_width" in data
        assert "screen_height" in data
        assert "timezone" in data
