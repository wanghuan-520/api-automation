# API Automation Testing Framework

## 项目概述 | Overview

这是一个现代化的API自动化测试框架，集成了主流测试工具和最佳实践。本框架专注于接口自动化测试，提供完整的测试解决方案。

This is a modern API automation testing framework, incorporating mainstream testing tools and best practices. The framework focuses on API automation testing and provides a complete testing solution.

## 特性 | Features

- 支持接口自动化测试 | Support API automation testing
- 支持多环境配置 | Support multi-environment configuration
- 支持测试报告生成 | Support test report generation
- 支持并发执行 | Support concurrent execution
- 支持数据驱动 | Support data-driven testing
- 支持CI/CD集成 | Support CI/CD integration
- 支持配置统一管理 | Support unified configuration management
- 支持环境变量配置 | Support environment variable configuration

## 技术栈 | Tech Stack

### 测试框架 | Test Framework
- Python 3.x
- pytest 7.4.3 (测试框架 | Testing framework)
- requests 2.31.0 (HTTP客户端 | HTTP client)
- urllib3 2.0.7 (HTTP库，支持重试机制 | HTTP library with retry support)
- pytest-html 3.2.0 (HTML报告生成 | HTML report generation)
- pytest-cov 4.1.0 (代码覆盖率 | Code coverage)
- pytest-xdist 3.3.1 (并行测试 | Parallel testing)
- python-dotenv 1.0.0 (环境变量管理 | Environment management)
- allure-pytest 2.13.2 (Allure报告 | Allure reporting)

## 项目结构 | Project Structure

```
api-automation/
├── config/            # 配置文件目录 | Configuration directory
│   └── config.yaml   # 环境配置 | Environment configuration
├── tests/             # 测试用例目录 | Test cases directory
│   └── (测试用例文件)  # Test case files
├── utils/             # 工具类目录 | Utility classes directory
│   ├── client.py     # API客户端 | API client
│   └── assert_utils.py  # 断言工具 | Assertion utilities
├── docs/              # 文档目录 | Documentation directory
├── reports/           # 测试报告目录 | Test reports directory
├── scripts/           # 脚本工具目录 | Script tools directory
├── libs/              # 库文件目录 | Library files directory
├── test-cases/        # 测试用例数据 | Test case data
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

# API配置 | API Configuration
API_TIMEOUT=30
API_MAX_RETRIES=3

# 认证配置 | Authentication Configuration
AUTH_TOKEN_URL=https://your-api.example.com/connect/token
TEST_USERNAME=your-username
TEST_PASSWORD=your-password
AUTH_CLIENT_ID=your-client-id
AUTH_SCOPE=your-scope
```

4. 运行测试 | Run Tests

```bash
# 运行所有测试 | Run all tests
pytest

# 运行指定测试 | Run specific tests
pytest tests/  # 运行所有测试 | Run all tests
pytest tests/ -k "test_name"  # 运行匹配的测试 | Run matching tests

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

- 使用数据驱动方式组织测试数据 | Use data-driven approach for test data
- 使用环境变量管理配置，避免硬编码 | Use environment variables for configuration, avoid hardcoding
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