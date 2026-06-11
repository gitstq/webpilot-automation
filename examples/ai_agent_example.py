"""
WebPilot AI Agent 使用示例

展示如何使用AI Agent实现自然语言驱动的浏览器操作。
"""

import asyncio
from webpilot import Browser, AIAgent


async def ai_plan_example():
    """AI规划操作示例"""
    # 初始化AI Agent（使用智谱AI）
    agent = AIAgent(
        api_key="your-api-key",
        model="glm-5.1",
        provider="zhipu",
    )

    # 让AI规划操作步骤
    actions = await agent.plan_actions(
        goal="在百度上搜索'Python教程'，并点击第一个结果",
        page_context={
            "current_url": "about:blank",
            "title": "空白页",
        },
    )

    print("AI规划的操作步骤:")
    for i, action in enumerate(actions):
        print(f"{i+1}. {action}")


async def ai_extract_example():
    """AI数据提取示例"""
    agent = AIAgent(
        api_key="your-api-key",
        model="glm-5.1",
        provider="zhipu",
    )

    # 模拟页面内容
    html_content = """
    <html>
    <body>
        <h1>产品列表</h1>
        <div class="product">
            <h2>iPhone 15</h2>
            <p class="price">5999元</p>
            <p class="brand">Apple</p>
        </div>
        <div class="product">
            <h2>MacBook Pro</h2>
            <p class="price">14999元</p>
            <p class="brand">Apple</p>
        </div>
    </body>
    </html>
    """

    schema = {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "string"},
                        "brand": {"type": "string"},
                    },
                },
            },
        },
    }

    # 使用AI提取数据
    data = await agent.extract_data(html_content, schema)
    print("提取的数据:")
    print(data)


async def ai_find_element_example():
    """AI元素查找示例"""
    agent = AIAgent(
        api_key="your-api-key",
        model="glm-5.1",
        provider="zhipu",
    )

    # 模拟页面HTML
    page_html = """
    <html>
    <body>
        <button id="submit-btn" class="btn primary">提交</button>
        <input type="text" id="username" placeholder="用户名">
        <a href="/login" class="link">登录</a>
    </body>
    </html>
    """

    # 让AI找到"提交按钮"的选择器
    selector = await agent.find_element("提交按钮", page_html)
    print(f"AI找到的选择器: {selector}")


async def ai_error_recovery_example():
    """AI错误恢复示例"""
    agent = AIAgent(
        api_key="your-api-key",
        model="glm-5.1",
        provider="zhipu",
    )

    # 模拟错误情况
    error = "ElementNotFoundError: 未找到元素 #search-input"
    current_state = {
        "current_url": "https://example.com",
        "last_action": "type #search-input 'hello'",
        "page_title": "示例网站",
    }

    # 获取恢复建议
    suggestion = await agent.handle_error(error, current_state)
    print("AI恢复建议:")
    print(suggestion)


if __name__ == "__main__":
    print("=== AI规划操作示例 ===")
    asyncio.run(ai_plan_example())

    print("\n=== AI数据提取示例 ===")
    asyncio.run(ai_extract_example())

    print("\n=== AI元素查找示例 ===")
    asyncio.run(ai_find_element_example())

    print("\n=== AI错误恢复示例 ===")
    asyncio.run(ai_error_recovery_example())
