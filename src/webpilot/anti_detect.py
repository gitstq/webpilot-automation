"""
反检测模块

提供浏览器指纹随机化、WebGL/Canvas噪声、时区语言模拟等反检测功能。
帮助自动化脚本绕过常见的反爬虫检测。
"""

import json
import random
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AntiDetectConfig:
    """反检测配置"""

    # 用户代理
    user_agent: Optional[str] = None

    # 屏幕分辨率
    screen_width: int = 1920
    screen_height: int = 1080
    screen_color_depth: int = 24

    # 时区
    timezone: str = "Asia/Shanghai"

    # 语言
    languages: list[str] = field(default_factory=lambda: ["zh-CN", "zh", "en"])

    # WebGL指纹
    webgl_vendor: str = "Intel Inc."
    webgl_renderer: str = "Intel Iris OpenGL Engine"

    # 字体
    fonts: list[str] = field(default_factory=lambda: [
        "Arial", "Arial Black", "Arial Narrow", "Book Antiqua",
        "Bookman Old Style", "Calibri", "Cambria", "Cambria Math",
        "Century", "Century Gothic", "Comic Sans MS", "Consolas",
        "Courier", "Courier New", "Georgia", "Helvetica",
        "Impact", "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Monotype Corsiva", "MS Gothic",
        "MS PGothic", "MS Reference Sans Serif", "MS Sans Serif",
        "MS Serif", "Palatino Linotype", "Segoe Print", "Segoe Script",
        "Segoe UI", "Segoe UI Light", "Segoe UI Semibold",
        "Segoe UI Symbol", "Tahoma", "Times", "Times New Roman",
        "Trebuchet MS", "Verdana", "Wingdings", "Wingdings 2",
        "Wingdings 3",
    ])

    # 插件
    plugins: list[dict[str, str]] = field(default_factory=lambda: [
        {"name": "Chrome PDF Plugin", "filename": "internal-pdf-viewer"},
        {"name": "Chrome PDF Viewer", "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai"},
        {"name": "Native Client", "filename": "internal-nacl-plugin"},
    ])

    # Canvas噪声
    canvas_noise: bool = True
    canvas_noise_level: float = 0.5

    # WebGL噪声
    webgl_noise: bool = True

    # 硬件并发数
    hardware_concurrency: int = 8

    # 设备内存
    device_memory: int = 8

    # 平台
    platform: str = "Win32"

    def to_js_script(self) -> str:
        """生成反检测JavaScript脚本"""
        config_json = json.dumps({
            "userAgent": self.user_agent,
            "screenWidth": self.screen_width,
            "screenHeight": self.screen_height,
            "screenColorDepth": self.screen_color_depth,
            "timezone": self.timezone,
            "languages": self.languages,
            "webglVendor": self.webgl_vendor,
            "webglRenderer": self.webgl_renderer,
            "fonts": self.fonts,
            "plugins": self.plugins,
            "canvasNoise": self.canvas_noise,
            "canvasNoiseLevel": self.canvas_noise_level,
            "webglNoise": self.webgl_noise,
            "hardwareConcurrency": self.hardware_concurrency,
            "deviceMemory": self.device_memory,
            "platform": self.platform,
        }, ensure_ascii=False)

        return f"""
        (function() {{
            const config = {config_json};

            // 覆盖navigator属性
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});

            Object.defineProperty(navigator, 'plugins', {{
                get: () => {{
                    return config.plugins.map((p, i) => ({{
                        name: p.name,
                        filename: p.filename,
                        description: p.name,
                        version: undefined,
                        length: 1,
                        item: function(index) {{ return this[index]; }},
                        namedItem: function(name) {{ return this[name]; }},
                        [i]: {{
                            name: p.name,
                            filename: p.filename,
                            description: p.name,
                            version: undefined,
                            length: 1,
                            item: function(index) {{ return this[index]; }},
                            namedItem: function(name) {{ return this[name]; }},
                        }}
                    }}));
                }}
            }});

            Object.defineProperty(navigator, 'languages', {{
                get: () => config.languages
            }});

            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => config.hardwareConcurrency
            }});

            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => config.deviceMemory
            }});

            Object.defineProperty(navigator, 'platform', {{
                get: () => config.platform
            }});

            // 覆盖screen属性
            Object.defineProperty(screen, 'width', {{
                get: () => config.screenWidth
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => config.screenHeight
            }});
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => config.screenColorDepth
            }});
            Object.defineProperty(screen, 'availWidth', {{
                get: () => config.screenWidth
            }});
            Object.defineProperty(screen, 'availHeight', {{
                get: () => config.screenHeight - 40
            }});

            // 覆盖chrome对象
            window.chrome = {{
                runtime: {{}},
                app: {{
                    isInstalled: false,
                    InstallState: {{
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    }},
                    RunningState: {{
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }}
                }},
                csi: function() {{}},
                loadTimes: function() {{
                    return {{
                        commitLoadTime: performance.timing.domContentLoadedEventStart / 1000,
                        connectionInfo: 'h2',
                        finishDocumentLoadTime: performance.timing.domContentLoadedEventEnd / 1000,
                        finishLoadTime: performance.timing.loadEventEnd / 1000,
                        firstPaintAfterLoadTime: 0,
                        firstPaintTime: performance.timing.domContentLoadedEventStart / 1000,
                        navigationType: 'Other',
                        npnNegotiatedProtocol: 'h2',
                        requestTime: performance.timing.requestStart / 1000,
                        startLoadTime: performance.timing.requestStart / 1000,
                        wasAlternateProtocolAvailable: false,
                        wasFetchedViaSpdy: true,
                        wasNpnNegotiated: true
                    }};
                }}
            }};

            // Canvas噪声
            if (config.canvasNoise) {{
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

                HTMLCanvasElement.prototype.toDataURL = function(type) {{
                    const context = this.getContext('2d');
                    if (context) {{
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        const data = imageData.data;
                        for (let i = 0; i < data.length; i += 4) {{
                            data[i] = Math.min(255, Math.max(0, data[i] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                            data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                            data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                        }}
                        context.putImageData(imageData, 0, 0);
                    }}
                    return originalToDataURL.apply(this, arguments);
                }};

                CanvasRenderingContext2D.prototype.getImageData = function() {{
                    const imageData = originalGetImageData.apply(this, arguments);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {{
                        data[i] = Math.min(255, Math.max(0, data[i] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                        data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                        data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (Math.random() - 0.5) * config.canvasNoiseLevel));
                    }}
                    return imageData;
                }};
            }}

            // WebGL指纹
            if (config.webglNoise) {{
                const getParameterProxy = {
                    apply(target, thisArg, args) {{
                        const param = args[0];
                        if (param === 37445) {{ // UNMASKED_VENDOR_WEBGL
                            return config.webglVendor;
                        }}
                        if (param === 37446) {{ // UNMASKED_RENDERER_WEBGL
                            return config.webglRenderer;
                        }}
                        return Reflect.apply(target, thisArg, args);
                    }}
                }};

                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = new Proxy(getParameter, getParameterProxy);

                if (window.WebGL2RenderingContext) {{
                    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
                    WebGL2RenderingContext.prototype.getParameter = new Proxy(getParameter2, getParameterProxy);
                }}
            }}

            // 时区覆盖
            const originalDate = Date;
            Date = class extends originalDate {{
                constructor(...args) {{
                    if (args.length === 0) {{
                        super();
                    }} else {{
                        super(...args);
                    }}
                }}

                toString() {{
                    return super.toString.apply(this, arguments).replace(
                        /\\b(UTC|GMT)[+-]\\d{{4}}\\b/,
                        config.timezone
                    );
                }}
            }};

            // 通知权限
            const originalNotification = window.Notification;
            Object.defineProperty(window, 'Notification', {{
                get: () => {{
                    return originalNotification;
                }}
            }});
            Object.defineProperty(Notification, 'permission', {{
                get: () => 'default'
            }});

            // Permissions API
            if (navigator.permissions) {{
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {{
                    return Promise.resolve({{
                        state: 'prompt',
                        onchange: null
                    }});
                }};
            }}
        }})();
        """

    @classmethod
    def random(cls) -> "AntiDetectConfig":
        """生成随机反检测配置"""
        configs = [
            # Windows Chrome
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "screen_width": 1920,
                "screen_height": 1080,
                "platform": "Win32",
                "webgl_vendor": "Google Inc. (NVIDIA)",
                "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            },
            # macOS Chrome
            {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "screen_width": 2560,
                "screen_height": 1440,
                "platform": "MacIntel",
                "webgl_vendor": "Apple Inc.",
                "webgl_renderer": "Apple M1",
            },
            # Linux Chrome
            {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "screen_width": 1920,
                "screen_height": 1080,
                "platform": "Linux x86_64",
                "webgl_vendor": "Intel Inc.",
                "webgl_renderer": "Intel Iris OpenGL Engine",
            },
        ]

        config_data = random.choice(configs)
        return cls(**config_data)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "user_agent": self.user_agent,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "screen_color_depth": self.screen_color_depth,
            "timezone": self.timezone,
            "languages": self.languages,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "fonts": self.fonts,
            "plugins": self.plugins,
            "canvas_noise": self.canvas_noise,
            "canvas_noise_level": self.canvas_noise_level,
            "webgl_noise": self.webgl_noise,
            "hardware_concurrency": self.hardware_concurrency,
            "device_memory": self.device_memory,
            "platform": self.platform,
        }
