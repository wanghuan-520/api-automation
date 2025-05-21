# API Automation Testing Framework

## 项目概述 | Overview

这是一个现代化的API自动化测试框架，集成了主流测试工具和最佳实践。本框架支持多种测试类型，包括接口自动化测试、UI自动化测试和性能测试。

This is a modern API automation testing framework, incorporating mainstream testing tools and best practices. The framework supports various testing types, including API automation tests, UI automation tests, and performance tests.

## 特性 | Features

- 支持接口自动化测试 | Support API automation testing
- 支持UI自动化测试 | Support UI automation testing
- 支持性能测试 | Support performance testing
- 支持多环境配置 | Support multi-environment configuration
- 支持测试报告生成 | Support test report generation
- 支持并发执行 | Support concurrent execution
- 支持数据驱动 | Support data-driven testing
- 支持CI/CD集成 | Support CI/CD integration

## 技术栈 | Tech Stack

### 测试框架 | Test Framework
- Python 3.x
- pytest 7.4.3 (测试框架 | Testing framework)
- requests 2.31.0 (HTTP客户端 | HTTP client)
- selenium 4.11.2 (UI自动化 | UI automation)
- pytest-html 3.2.0 (HTML报告生成 | HTML report generation)
- pytest-cov 4.1.0 (代码覆盖率 | Code coverage)
- pytest-xdist 3.3.1 (并行测试 | Parallel testing)
- python-dotenv 1.0.0 (环境变量管理 | Environment management)

## 项目结构 | Project Structure

```
api-automation/
├── src/                # 源代码目录 | Source code directory
│   ├── api/           # API接口封装 | API interface encapsulation
│   ├── pages/         # 页面对象 | Page objects
│   └── utils/         # 工具类 | Utility classes
├── tests/             # 测试用例目录 | Test cases directory
│   ├── api_tests/     # 接口测试用例 | API test cases
│   ├── ui_tests/      # UI测试用例 | UI test cases
│   └── perf_tests/    # 性能测试用例 | Performance test cases
├── config/            # 配置文件目录 | Configuration directory
│   ├── env/          # 环境配置 | Environment configuration
│   └── data/         # 测试数据 | Test data
├── reports/           # 测试报告目录 | Test reports directory
│   ├── html/         # HTML报告 | HTML reports
│   └── allure/       # Allure报告 | Allure reports
├── logs/              # 日志目录 | Logs directory
├── scripts/           # 脚本工具目录 | Script tools directory
├── requirements.txt   # Python依赖 | Python dependencies
├── pytest.ini        # Pytest配置 | Pytest configuration
├── conftest.py       # Pytest全局配置 | Pytest global configuration
└── README.md         # 项目说明文档 | Project documentation
```

## 快速开始 | Quick Start

1. 克隆项目 | Clone the project
```bash
git clone https://github.com/your-org/api-automation.git
cd api-automation
```

2. 安装依赖 | Install Dependencies
```bash
# 创建并激活虚拟环境 | Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖包 | Install dependencies
pip install -r requirements.txt
```

3. 配置环境变量 | Configure Environment Variables
创建 `.env` 文件并设置必要的环境变量：
Create a `.env` file and set necessary environment variables:

```ini
# API配置 | API Configuration
API_BASE_URL=http://localhost:8000
API_VERSION=v1

# 测试环境 | Test Environment
TEST_ENV=dev
BROWSER_TYPE=chrome

# 其他配置 | Other Configuration
HEADLESS=True
SCREENSHOT_DIR=./reports/screenshots
```

4. 运行测试 | Run Tests

```bash
# 运行所有测试 | Run all tests
pytest

# 运行指定测试 | Run specific tests
pytest tests/api_tests/  # 运行API测试 | Run API tests
pytest tests/ui_tests/   # 运行UI测试 | Run UI tests

# 生成HTML报告 | Generate HTML report
pytest --html=reports/html/report.html

# 生成覆盖率报告 | Generate coverage report
pytest --cov=src tests/ --cov-report=html:reports/coverage

# 并行执行测试 | Run tests in parallel
pytest -n auto
```

## 测试报告 | Test Reports

测试执行后，可以在以下位置查看报告：
After test execution, reports can be found at:

- HTML测试报告 | HTML Test Report: `reports/html/report.html`
- 覆盖率报告 | Coverage Report: `reports/coverage/index.html`
- Allure报告 | Allure Report: `reports/allure`
- 测试日志 | Test Logs: `logs/test.log`

## 最佳实践 | Best Practices

- 使用Page Object模式组织UI测试 | Use Page Object pattern for UI tests
- 使用数据驱动方式组织测试数据 | Use data-driven approach for test data
- 保持测试用例的独立性 | Keep test cases independent
- 合理使用夹具(fixtures)复用代码 | Properly use fixtures for code reuse
- 及时清理测试数据 | Clean up test data timely

## 贡献指南 | Contributing

欢迎提交 Pull Requests 和 Issues。在提交之前，请确保：
Pull Requests and Issues are welcome. Before submitting, please ensure:

1. 所有测试都通过 | All tests pass
2. 代码符合项目规范 | Code follows project conventions
3. 更新相关文档 | Documentation is updated
4. 添加必要的测试用例 | Add necessary test cases

## 许可证 | License

ISC License 