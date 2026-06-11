"""
国内平台适配器

提供对国内主流网站（微信、抖音、小红书、B站等）的专用API适配。
简化这些平台的自动化操作复杂度。
"""

from .wechat import WechatAdapter
from .douyin import DouyinAdapter
from .xiaohongshu import XiaohongshuAdapter
from .bilibili import BilibiliAdapter

__all__ = [
    "WechatAdapter",
    "DouyinAdapter",
    "XiaohongshuAdapter",
    "BilibiliAdapter",
]
