"""
Chrome DevTools Protocol (CDP) 客户端

通过WebSocket与Chrome/Chromium浏览器通信，实现CDP命令的发送和事件的接收。
支持异步操作、自动重连、请求-响应匹配。
"""

import asyncio
import json
import uuid
from typing import Any, Callable, Coroutine, Optional

import websockets
from websockets.client import WebSocketClientProtocol

from .exceptions import CDPError, TimeoutError


class CDPClient:
    """CDP WebSocket客户端"""

    def __init__(
        self,
        ws_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.ws_url = ws_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.ws: Optional[WebSocketClientProtocol] = None
        self._message_id = 0
        self._pending: dict[str, asyncio.Future[Any]] = {}
        self._event_handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self._listen_task: Optional[asyncio.Task[None]] = None
        self._closed = False

    async def connect(self) -> None:
        """建立WebSocket连接"""
        retries = 0
        last_error: Optional[Exception] = None

        while retries < self.max_retries:
            try:
                self.ws = await websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                )
                self._closed = False
                self._listen_task = asyncio.create_task(self._listen())
                return
            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    await asyncio.sleep(0.5 * retries)

        raise CDPError(
            f"无法连接到CDP WebSocket ({self.ws_url}): {last_error}"
        )

    async def disconnect(self) -> None:
        """断开WebSocket连接"""
        self._closed = True

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self.ws:
            await self.ws.close()
            self.ws = None

        # 清理所有pending请求
        for future in self._pending.values():
            if not future.done():
                future.set_exception(CDPError("连接已关闭"))
        self._pending.clear()

    async def send(
        self,
        method: str,
        params: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """发送CDP命令并等待响应"""
        if not self.ws or self._closed:
            raise CDPError("CDP客户端未连接")

        self._message_id += 1
        msg_id = str(self._message_id)

        message: dict[str, Any] = {
            "id": int(msg_id),
            "method": method,
        }
        if params:
            message["params"] = params
        if session_id:
            message["sessionId"] = session_id

        future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future

        try:
            await self.ws.send(json.dumps(message))
            return await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise TimeoutError(f"CDP命令超时: {method}")
        except Exception as e:
            self._pending.pop(msg_id, None)
            raise CDPError(f"CDP命令执行失败: {e}")

    def on(
        self,
        event: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """注册事件处理器"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def off(
        self,
        event: str,
        handler: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> None:
        """注销事件处理器"""
        if event in self._event_handlers:
            if handler is None:
                self._event_handlers[event].clear()
            else:
                self._event_handlers[event] = [
                    h for h in self._event_handlers[event] if h != handler
                ]

    async def _listen(self) -> None:
        """监听WebSocket消息"""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                if self._closed:
                    break
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    continue
        except websockets.exceptions.ConnectionClosed:
            if not self._closed:
                # 尝试重连
                await self._reconnect()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if not self._closed:
                raise CDPError(f"CDP监听错误: {e}")

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """处理接收到的消息"""
        # 响应消息
        if "id" in data:
            msg_id = str(data["id"])
            future = self._pending.pop(msg_id, None)
            if future and not future.done():
                if "error" in data:
                    error = data["error"]
                    future.set_exception(
                        CDPError(f"{error.get('message', 'Unknown error')} (code: {error.get('code', 'N/A')})")
                    )
                else:
                    future.set_result(data.get("result", {}))

        # 事件消息
        elif "method" in data:
            event = data["method"]
            params = data.get("params", {})
            handlers = self._event_handlers.get(event, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(params))
                    else:
                        handler(params)
                except Exception:
                    # 事件处理器异常不应影响主流程
                    pass

    async def _reconnect(self) -> None:
        """自动重连"""
        try:
            await self.disconnect()
            await self.connect()
        except Exception:
            pass

    async def __aenter__(self) -> "CDPClient":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()
