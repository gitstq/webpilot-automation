"""
浏览器管理模块

负责Chrome/Chromium浏览器的启动、管理和关闭。
支持无头模式、反检测配置、代理设置等高级功能。
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

import aiohttp

from .cdp_client import CDPClient
from .exceptions import BrowserError, CDPError
from .page import Page


class Browser:
    """浏览器实例"""

    def __init__(
        self,
        cdp_client: CDPClient,
        process: subprocess.Popen[str],
        user_data_dir: str,
        debug_port: int,
    ) -> None:
        self._cdp = cdp_client
        self._process = process
        self._user_data_dir = user_data_dir
        self._debug_port = debug_port
        self._pages: list[Page] = []
        self._closed = False

    @classmethod
    async def launch(
        cls,
        executable_path: Optional[str] = None,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        debug_port: Optional[int] = None,
        args: Optional[list[str]] = None,
        proxy: Optional[str] = None,
        window_size: tuple[int, int] = (1920, 1080),
        anti_detect: bool = False,
        **kwargs: Any,
    ) -> "Browser":
        """
        启动浏览器

        Args:
            executable_path: Chrome/Chromium可执行文件路径，默认自动查找
            headless: 是否无头模式
            user_data_dir: 用户数据目录
            debug_port: 调试端口
            args: 额外的启动参数
            proxy: 代理服务器地址
            window_size: 窗口大小
            anti_detect: 是否启用反检测
            **kwargs: 其他参数

        Returns:
            Browser实例
        """
        # 查找Chrome/Chromium
        if not executable_path:
            executable_path = cls._find_chrome()
            if not executable_path:
                raise BrowserError("未找到Chrome或Chromium，请指定executable_path")

        # 创建临时用户数据目录
        if not user_data_dir:
            user_data_dir = tempfile.mkdtemp(prefix="webpilot_user_data_")

        if not debug_port:
            debug_port = cls._find_free_port()

        # 构建启动参数
        launch_args = [
            executable_path,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data_dir}",
            f"--window-size={window_size[0]},{window_size[1]}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-blink-features=AutomationControlled",
        ]

        if headless:
            launch_args.append("--headless=new")

        if proxy:
            launch_args.append(f"--proxy-server={proxy}")

        # 反检测配置
        if anti_detect:
            launch_args.extend([
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-blink-features=AutomationControlled",
            ])

        if args:
            launch_args.extend(args)

        # 启动浏览器进程
        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    launch_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                process = subprocess.Popen(
                    launch_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
        except Exception as e:
            raise BrowserError(f"启动浏览器失败: {e}")

        # 等待调试端口就绪
        ws_url = await cls._wait_for_ws_endpoint(debug_port)
        if not ws_url:
            process.kill()
            raise BrowserError("无法获取CDP WebSocket地址")

        # 创建CDP客户端
        cdp_client = CDPClient(ws_url, **kwargs)
        await cdp_client.connect()

        browser = cls(cdp_client, process, user_data_dir, debug_port)

        # 应用反检测脚本
        if anti_detect:
            await browser._apply_anti_detect()

        return browser

    async def new_page(self) -> Page:
        """创建新页面"""
        result = await self._cdp.send("Target.createTarget", {"url": "about:blank"})
        target_id = result["targetId"]

        # 获取页面session
        session_result = await self._cdp.send(
            "Target.attachToTarget",
            {"targetId": target_id, "flatten": True},
        )
        session_id = session_result["sessionId"]

        page = Page(self._cdp, target_id, session_id)
        self._pages.append(page)
        return page

    async def pages(self) -> list[Page]:
        """获取所有页面"""
        return self._pages.copy()

    async def close(self) -> None:
        """关闭浏览器"""
        if self._closed:
            return

        self._closed = True

        # 关闭所有页面
        for page in self._pages:
            await page.close()
        self._pages.clear()

        # 断开CDP连接
        await self._cdp.disconnect()

        # 终止浏览器进程
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

        # 清理临时用户数据目录
        if self._user_data_dir and os.path.exists(self._user_data_dir):
            shutil.rmtree(self._user_data_dir, ignore_errors=True)

    @property
    def is_connected(self) -> bool:
        """检查浏览器是否连接"""
        return not self._closed and self._process.poll() is None

    async def _apply_anti_detect(self) -> None:
        """应用反检测脚本"""
        # 覆盖navigator.webdriver属性
        script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        window.chrome = {
            runtime: {},
            app: {}
        };
        """
        # 在所有目标上执行
        targets = await self._cdp.send("Target.getTargets")
        for target in targets.get("targetInfos", []):
            if target["type"] == "page":
                try:
                    await self._cdp.send(
                        "Runtime.evaluate",
                        {
                            "expression": script,
                            "contextId": 1,
                        },
                    )
                except CDPError:
                    pass

    @staticmethod
    def _find_chrome() -> Optional[str]:
        """查找Chrome/Chromium可执行文件"""
        system = platform.system()

        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Chromium\Application\chromium.exe",
            ]
            for path in paths:
                if "{}" in path:
                    import getpass
                    path = path.format(getpass.getuser())
                if os.path.exists(path):
                    return path

        elif system == "Darwin":
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
            ]
            for path in paths:
                if os.path.exists(path):
                    return path

        elif system == "Linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ]
            for path in paths:
                if os.path.exists(path):
                    return path

        # 尝试在PATH中查找
        for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
            path = shutil.which(name)
            if path:
                return path

        return None

    @staticmethod
    def _find_free_port() -> int:
        """查找可用端口"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    @staticmethod
    async def _wait_for_ws_endpoint(port: int, timeout: float = 30.0) -> Optional[str]:
        """等待WebSocket端点就绪"""
        start_time = asyncio.get_event_loop().time()
        url = f"http://localhost:{port}/json/version"

        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=2) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("webSocketDebuggerUrl")
            except Exception:
                pass
            await asyncio.sleep(0.5)

        return None

    async def __aenter__(self) -> "Browser":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
