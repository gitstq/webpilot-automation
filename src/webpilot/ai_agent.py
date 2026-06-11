"""
AI Agent模块

集成大语言模型（支持OpenAI和智谱AI），实现自然语言驱动的浏览器操作。
支持智能元素识别、自动操作规划、错误恢复等功能。
"""

import json
from typing import Any, Optional

from .exceptions import AIAgentError


class AIAgent:
    """AI驱动的浏览器操作代理"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-5.1",
        base_url: Optional[str] = None,
        provider: str = "zhipu",
    ) -> None:
        """
        初始化AI Agent

        Args:
            api_key: API密钥
            model: 模型名称
            base_url: 自定义API地址
            provider: 提供商 (zhipu/openai)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.provider = provider
        self._client: Any = None

    async def _get_client(self) -> Any:
        """获取API客户端"""
        if self._client is not None:
            return self._client

        if self.provider == "zhipu":
            try:
                from zhipuai import ZhipuAI
                self._client = ZhipuAI(api_key=self.api_key)
            except ImportError:
                raise AIAgentError("未安装zhipuai包，请运行: pip install zhipuai")
        elif self.provider == "openai":
            try:
                import openai
                self._client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except ImportError:
                raise AIAgentError("未安装openai包，请运行: pip install openai")
        else:
            raise AIAgentError(f"不支持的AI提供商: {self.provider}")

        return self._client

    async def plan_actions(
        self,
        goal: str,
        page_context: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        规划操作步骤

        Args:
            goal: 用户目标描述
            page_context: 当前页面上下文

        Returns:
            操作步骤列表
        """
        context_str = json.dumps(page_context, ensure_ascii=False, indent=2) if page_context else "无"

        prompt = f"""你是一个浏览器自动化专家。请根据用户目标和当前页面上下文，规划详细的操作步骤。

用户目标: {goal}

当前页面上下文:
{context_str}

请返回JSON格式的操作步骤列表，每个步骤包含:
- action: 操作类型 (goto/click/type/wait/extract/screenshot)
- selector: CSS选择器 (如适用)
- value: 输入值 (如适用)
- description: 操作描述

示例输出:
[
    {{
        "action": "goto",
        "value": "https://example.com",
        "description": "导航到目标网站"
    }},
    {{
        "action": "click",
        "selector": "#search-button",
        "description": "点击搜索按钮"
    }}
]

请只返回JSON数组，不要其他内容。"""

        response = await self._chat_completion(prompt)

        try:
            # 提取JSON部分
            json_str = self._extract_json(response)
            actions = json.loads(json_str)
            return actions if isinstance(actions, list) else []
        except json.JSONDecodeError as e:
            raise AIAgentError(f"无法解析AI响应: {e}")

    async def extract_data(
        self,
        html_content: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        智能提取页面数据

        Args:
            html_content: 页面HTML内容
            schema: 数据结构定义

        Returns:
            提取的数据
        """
        prompt = f"""从以下网页内容中提取结构化数据。

网页内容:
{html_content[:8000]}

数据结构要求:
{json.dumps(schema, ensure_ascii=False, indent=2)}

请返回符合上述结构的JSON数据，只返回JSON，不要其他内容。"""

        response = await self._chat_completion(prompt)

        try:
            json_str = self._extract_json(response)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise AIAgentError(f"无法解析提取的数据: {e}")

    async def find_element(
        self,
        description: str,
        page_html: str,
    ) -> Optional[str]:
        """
        智能查找元素选择器

        Args:
            description: 元素描述
            page_html: 页面HTML

        Returns:
            CSS选择器或None
        """
        prompt = f"""根据元素描述，从页面HTML中找到最匹配的CSS选择器。

元素描述: {description}

页面HTML片段:
{page_html[:5000]}

请返回最可能匹配该元素的CSS选择器，只返回选择器字符串，不要其他内容。
如果无法确定，返回"unknown"。"""

        response = await self._chat_completion(prompt)
        selector = response.strip().strip('"').strip("'")

        if selector == "unknown":
            return None
        return selector

    async def handle_error(
        self,
        error: str,
        current_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        错误恢复建议

        Args:
            error: 错误信息
            current_state: 当前状态

        Returns:
            恢复建议
        """
        prompt = f"""浏览器自动化过程中遇到错误，请提供恢复建议。

错误信息: {error}

当前状态:
{json.dumps(current_state, ensure_ascii=False, indent=2)}

请返回JSON格式的恢复建议:
{{
    "analysis": "错误原因分析",
    "recovery_action": "建议的恢复操作",
    "alternative_approach": "备选方案"
}}

只返回JSON，不要其他内容。"""

        response = await self._chat_completion(prompt)

        try:
            json_str = self._extract_json(response)
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "analysis": "无法分析错误",
                "recovery_action": "重试当前操作",
                "alternative_approach": "手动处理",
            }

    async def _chat_completion(self, prompt: str) -> str:
        """调用聊天补全API"""
        client = await self._get_client()

        if self.provider == "zhipu":
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的浏览器自动化助手。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                raise AIAgentError(f"智谱AI API调用失败: {e}")

        elif self.provider == "openai":
            try:
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的浏览器自动化助手。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                raise AIAgentError(f"OpenAI API调用失败: {e}")

        return ""

    @staticmethod
    def _extract_json(text: str) -> str:
        """从文本中提取JSON"""
        # 尝试找到JSON数组或对象
        text = text.strip()

        # 移除markdown代码块标记
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # 找到JSON开始位置
        start_idx = -1
        for i, char in enumerate(text):
            if char in "[{":
                start_idx = i
                break

        if start_idx == -1:
            return text

        # 找到JSON结束位置
        end_idx = -1
        depth = 0
        in_string = False
        escape_next = False

        for i in range(start_idx, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if char in "[{":
                depth += 1
            elif char in "}]":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        if end_idx == -1:
            return text[start_idx:]

        return text[start_idx:end_idx + 1]
