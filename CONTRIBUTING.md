# 贡献指南

感谢您对 WebPilot 项目的关注！我们欢迎并感谢所有形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请通过 [GitHub Issues](https://github.com/yourusername/webpilot/issues) 提交。

提交问题时，请包含以下信息：
- 问题的清晰描述
- 复现步骤
- 期望行为与实际行为
- 环境信息（操作系统、Python版本、Chrome版本）
- 相关代码片段或错误日志

### 提交代码

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/webpilot.git
cd webpilot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src tests
ruff check src tests
```

### 代码规范

- 遵循 PEP 8 风格指南
- 使用类型注解
- 编写清晰的文档字符串
- 保持测试覆盖率

## 行为准则

本项目采用 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。
