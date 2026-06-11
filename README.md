# 🚀 WebPilot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/CDP-Chrome%20DevTools-orange?logo=google-chrome" alt="CDP">
  <img src="https://img.shields.io/badge/AI-GLM--5.1%20%7C%20GPT-purple?logo=openai" alt="AI">
</p>

<p align="center">
  <b>新一代CDP浏览器自动化引擎</b><br>
  AI驱动 · 反检测增强 · 国内平台适配
</p>

---

## 🎉 项目介绍

WebPilot 是一个基于 **Chrome DevTools Protocol (CDP)** 的浏览器自动化引擎，无需 WebDriver 即可实现强大的浏览器控制。相比传统 Selenium/Playwright，WebPilot 具有以下独特优势：

- 🧠 **AI智能驱动** — 集成大语言模型，支持自然语言操作规划、智能元素识别、自动数据提取
- 🛡️ **反检测增强** — 内置指纹随机化、Canvas/WebGL噪声、时区语言模拟等反检测技术
- 🇨🇳 **国内平台适配** — 提供微信、抖音、小红书、B站等国内主流平台的专用API
- 📹 **录制回放系统** — 类似Playwright codegen，支持操作录制和代码生成
- ⚡ **纯异步架构** — 基于asyncio，支持高并发操作

## ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| CDP驱动 | 直接通过Chrome DevTools Protocol控制浏览器，无需WebDriver | ✅ |
| AI Agent | 支持OpenAI/智谱AI，自然语言驱动浏览器操作 | ✅ |
| 反检测 | 指纹随机化、Canvas噪声、WebGL伪装、时区模拟 | ✅ |
| 国内适配 | 微信、抖音、小红书、B站专用API | ✅ |
| 录制回放 | 操作录制、Python代码生成、JSON脚本导出 | ✅ |
| 结构化提取 | Pydantic模型驱动的数据提取 | ✅ |
| 截图/PDF | 页面截图、元素截图、完整页面、PDF生成 | ✅ |
| 智能等待 | 元素等待、可见性检查、超时处理 | ✅ |

## 🚀 快速开始

### 安装

```bash
# 基础安装
pip install webpilot

# 包含AI功能
pip install webpilot[ai]

# 开发安装
pip install webpilot[all]
```

### 基础用法

```python
import asyncio
from webpilot import Browser

async def main():
    # 启动浏览器
    browser = await Browser.launch(headless=True)
    page = await browser.new_page()
    
    # 导航到网页
    await page.goto("https://example.com")
    
    # 获取标题
    title = await page.title()
    print(f"标题: {title}")
    
    # 截图
    await page.screenshot("example.png")
    
    # 关闭浏览器
    await browser.close()

asyncio.run(main())
```

### 反检测模式

```python
# 启用反检测，绕过大多数反爬虫检测
browser = await Browser.launch(
    headless=True,
    anti_detect=True,
)
```

### AI智能操作

```python
from webpilot import AIAgent

agent = AIAgent(api_key="your-api-key", model="glm-5.1")

# AI规划操作步骤
actions = await agent.plan_actions(
    goal="在百度上搜索'Python教程'，点击第一个结果"
)
```

### 国内平台适配

```python
from webpilot.adapters import DouyinAdapter

# 抖音搜索
douyin = DouyinAdapter(page)
videos = await douyin.search("Python教程")
```

## 📖 详细使用指南

### 浏览器管理

```python
from webpilot import Browser

# 启动配置
browser = await Browser.launch(
    executable_path="/usr/bin/google-chrome",  # 自定义Chrome路径
    headless=True,                              # 无头模式
    proxy="http://proxy:8080",                 # 代理设置
    window_size=(1920, 1080),                  # 窗口大小
    anti_detect=True,                          # 启用反检测
)

# 多页面管理
page1 = await browser.new_page()
page2 = await browser.new_page()
pages = await browser.pages()

# 关闭
await browser.close()
```

### 页面操作

```python
# 导航
await page.goto("https://example.com", wait_until="networkidle")

# 元素查找
element = await page.query_selector("#button")
elements = await page.query_selector_all(".item")

# 等待元素
await page.wait_for_selector("#loading", timeout=30)

# 点击和输入
await page.click("#submit")
await page.type("#input", "hello world", delay=0.1)

# JavaScript执行
result = await page.evaluate("document.title")

# 截图和PDF
await page.screenshot("page.png", full_page=True)
await page.pdf("page.pdf")
```

### 元素操作

```python
element = await page.query_selector("#button")

# 点击
await element.click()

# 输入文本
await element.type("hello", delay=0.05)

# 获取属性
text = await element.text_content()
html = await element.inner_html()
href = await element.get_attribute("href")

# 滚动到视图
await element.scroll_into_view()

# 悬停
await element.hover()
```

### 反检测配置

```python
from webpilot.anti_detect import AntiDetectConfig

# 使用随机配置
config = AntiDetectConfig.random()

# 自定义配置
config = AntiDetectConfig(
    user_agent="Mozilla/5.0 ...",
    screen_width=1920,
    screen_height=1080,
    timezone="Asia/Shanghai",
    webgl_vendor="Intel Inc.",
    canvas_noise=True,
)
```

### 录制回放

```python
from webpilot.recorder import Recorder

recorder = Recorder()
recorder.start()

# 记录操作
recorder.record_goto("https://example.com")
recorder.record_click("#button")
recorder.record_type("#input", "hello")

# 生成代码
code = recorder.to_python_code()
recorder.save("recording.json")

# 回放
from webpilot.recorder import Player
player = Player(page)
await player.play(actions)
```

## 💡 设计思路与迭代规划

### 架构设计

```
WebPilot
├── CDP Client (WebSocket通信)
├── Browser Manager (进程管理)
├── Page Controller (页面操作)
├── Element Handler (元素交互)
├── Anti-Detect Engine (反检测)
├── AI Agent (智能驱动)
├── Recorder/Player (录制回放)
└── Platform Adapters (平台适配)
```

### 迭代规划

- [x] v1.0.0 - 核心CDP驱动、基础操作、反检测
- [ ] v1.1.0 - 移动端H5支持、触屏事件模拟
- [ ] v1.2.0 - 可视化调试面板、实时CDP监控
- [ ] v1.3.0 - 更多国内平台适配（淘宝、京东、知乎）
- [ ] v2.0.0 - 多Agent协作、分布式浏览器集群

## 📦 打包与部署

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/webpilot-automation.git
cd webpilot-automation

# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
black src tests
ruff check src tests
mypy src
```

### 构建发布

```bash
# 构建包
python -m build

# 上传到PyPI
python -m twine upload dist/*
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<p align="center">
  Made with ❤️ by WebPilot Team
</p>
