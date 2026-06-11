# 🚀 WebPilot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/CDP-Chrome%20DevTools-orange?logo=google-chrome" alt="CDP">
  <img src="https://img.shields.io/badge/AI-GLM--5.1%20%7C%20GPT-purple?logo=openai" alt="AI">
</p>

<p align="center">
  <b>Next-Generation CDP Browser Automation Engine</b><br>
  AI-Powered · Anti-Detection Enhanced · Domestic Platform Adapted
</p>

---

## 🎉 Introduction

WebPilot is a browser automation engine based on **Chrome DevTools Protocol (CDP)**, enabling powerful browser control without WebDriver. Compared to traditional Selenium/Playwright, WebPilot offers unique advantages:

- 🧠 **AI-Powered** — Integrated LLM support for natural language operation planning, intelligent element recognition, and automated data extraction
- 🛡️ **Anti-Detection** — Built-in fingerprint randomization, Canvas/WebGL noise, timezone and language simulation
- 🇨🇳 **Domestic Platform Adapters** — Dedicated APIs for WeChat, Douyin (TikTok), Xiaohongshu, Bilibili, and more
- 📹 **Recording & Playback** — Playwright-like codegen with operation recording and code generation
- ⚡ **Pure Async Architecture** — Based on asyncio for high-concurrency operations

## ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| CDP-Driven | Direct browser control via Chrome DevTools Protocol, no WebDriver needed | ✅ |
| AI Agent | OpenAI/Zhipu AI support, natural language driven browser operations | ✅ |
| Anti-Detection | Fingerprint randomization, Canvas noise, WebGL spoofing, timezone simulation | ✅ |
| Domestic Adapters | WeChat, Douyin, Xiaohongshu, Bilibili dedicated APIs | ✅ |
| Recording | Operation recording, Python code generation, JSON script export | ✅ |
| Structured Extraction | Pydantic model-driven data extraction | ✅ |
| Screenshot/PDF | Page screenshot, element screenshot, full page, PDF generation | ✅ |
| Smart Waiting | Element waiting, visibility checking, timeout handling | ✅ |

## 🚀 Quick Start

### Installation

```bash
# Base installation
pip install webpilot

# With AI features
pip install webpilot[ai]

# Development installation
pip install webpilot[all]
```

### Basic Usage

```python
import asyncio
from webpilot import Browser

async def main():
    # Launch browser
    browser = await Browser.launch(headless=True)
    page = await browser.new_page()
    
    # Navigate to webpage
    await page.goto("https://example.com")
    
    # Get title
    title = await page.title()
    print(f"Title: {title}")
    
    # Screenshot
    await page.screenshot("example.png")
    
    # Close browser
    await browser.close()

asyncio.run(main())
```

### Anti-Detection Mode

```python
# Enable anti-detection to bypass most anti-bot detection
browser = await Browser.launch(
    headless=True,
    anti_detect=True,
)
```

### AI-Powered Operations

```python
from webpilot import AIAgent

agent = AIAgent(api_key="your-api-key", model="glm-5.1")

# AI plans operation steps
actions = await agent.plan_actions(
    goal="Search for 'Python tutorial' on Baidu and click the first result"
)
```

### Domestic Platform Adapters

```python
from webpilot.adapters import DouyinAdapter

# Douyin search
douyin = DouyinAdapter(page)
videos = await douyin.search("Python tutorial")
```

## 📖 Detailed Guide

### Browser Management

```python
from webpilot import Browser

# Launch configuration
browser = await Browser.launch(
    executable_path="/usr/bin/google-chrome",  # Custom Chrome path
    headless=True,                              # Headless mode
    proxy="http://proxy:8080",                 # Proxy settings
    window_size=(1920, 1080),                  # Window size
    anti_detect=True,                          # Enable anti-detection
)

# Multi-page management
page1 = await browser.new_page()
page2 = await browser.new_page()
pages = await browser.pages()

# Close
await browser.close()
```

### Page Operations

```python
# Navigation
await page.goto("https://example.com", wait_until="networkidle")

# Element query
element = await page.query_selector("#button")
elements = await page.query_selector_all(".item")

# Wait for element
await page.wait_for_selector("#loading", timeout=30)

# Click and type
await page.click("#submit")
await page.type("#input", "hello world", delay=0.1)

# JavaScript execution
result = await page.evaluate("document.title")

# Screenshot and PDF
await page.screenshot("page.png", full_page=True)
await page.pdf("page.pdf")
```

### Element Operations

```python
element = await page.query_selector("#button")

# Click
await element.click()

# Type text
await element.type("hello", delay=0.05)

# Get attributes
text = await element.text_content()
html = await element.inner_html()
href = await element.get_attribute("href")

# Scroll into view
await element.scroll_into_view()

# Hover
await element.hover()
```

### Anti-Detection Configuration

```python
from webpilot.anti_detect import AntiDetectConfig

# Use random configuration
config = AntiDetectConfig.random()

# Custom configuration
config = AntiDetectConfig(
    user_agent="Mozilla/5.0 ...",
    screen_width=1920,
    screen_height=1080,
    timezone="Asia/Shanghai",
    webgl_vendor="Intel Inc.",
    canvas_noise=True,
)
```

### Recording & Playback

```python
from webpilot.recorder import Recorder

recorder = Recorder()
recorder.start()

# Record operations
recorder.record_goto("https://example.com")
recorder.record_click("#button")
recorder.record_type("#input", "hello")

# Generate code
code = recorder.to_python_code()
recorder.save("recording.json")

# Playback
from webpilot.recorder import Player
player = Player(page)
await player.play(actions)
```

## 💡 Design & Roadmap

### Architecture

```
WebPilot
├── CDP Client (WebSocket Communication)
├── Browser Manager (Process Management)
├── Page Controller (Page Operations)
├── Element Handler (Element Interaction)
├── Anti-Detect Engine (Anti-Detection)
├── AI Agent (Intelligent Driving)
├── Recorder/Player (Recording & Playback)
└── Platform Adapters (Platform Adaptation)
```

### Roadmap

- [x] v1.0.0 - Core CDP driver, basic operations, anti-detection
- [ ] v1.1.0 - Mobile H5 support, touch event simulation
- [ ] v1.2.0 - Visual debugging panel, real-time CDP monitoring
- [ ] v1.3.0 - More domestic platform adapters (Taobao, JD, Zhihu)
- [ ] v2.0.0 - Multi-agent collaboration, distributed browser cluster

## 📦 Packaging & Deployment

### Local Development

```bash
# Clone repository
git clone https://github.com/gitstq/webpilot-automation.git
cd webpilot-automation

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code linting
black src tests
ruff check src tests
mypy src
```

### Build & Release

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## 🤝 Contributing

We welcome all forms of contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by WebPilot Team
</p>
