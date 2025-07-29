# API自动化测试套件

## 🌌 测试套件概述

基于 `api_testing_priotiy.md` 文档生成的完整API测试套件，按照业务优先级和重要性进行分类测试。

## 📊 测试分类

### 🔥 核心业务接口 (最高优先级)
- **文件**: `tests/api_tests/test_core_apis.py`
- **标记**: `@pytest.mark.core`
- **包含接口**:
  - `POST /api/godgpt/create-session` - 会话创建（前置条件）
  - `POST /api/gotgpt/chat` - AI聊天核心功能（需要session）
  - `GET /api/godgpt/account` - 用户信息获取
  - `PUT /api/godgpt/account` - 用户信息更新
  - `GET /api/godgpt/session-list` - 会话列表
  - `GET /api/godgpt/chat/{sessionId}` - 聊天历史（需要session）
  - `DELETE /api/godgpt/chat/{sessionId}` - 删除会话（需要session）
  - `GET /api/godgpt/session-info/{sessionId}` - 会话信息（需要session）
  - `POST /api/account/check-email-registered` - 邮箱注册检查
  - `GET /api/account/logout` - 用户登出
  - JWT认证流程

### ⚠️ 重要业务接口 (高优先级)
- **文件**: `tests/api_tests/test_important_apis.py`
- **标记**: `@pytest.mark.important`
- **包含接口**:
  - 支付系统接口 (产品列表、收据验证、结账会话、Apple订阅)
  - 会话管理接口 (聊天历史、删除会话、会话信息) - 需要session
  - 访客模式接口 (访客会话创建、访客聊天) - 需要访客session

### 📊 功能业务接口 (中优先级)
- **文件**: `tests/api_tests/test_functional_apis.py`
- **标记**: `@pytest.mark.functional`
- **包含接口**:
  - 邀请奖励系统 (邀请信息、邀请码兑换、积分历史)
  - 分享功能 (分享关键词、分享内容)
  - 音频功能 (语音聊天) - 需要session

### 🔧 系统管理接口 (低优先级)
- **文件**: `tests/api_tests/test_system_apis.py`
- **标记**: `@pytest.mark.system`
- **包含接口**:
  - 系统配置 (系统提示词获取/更新)
  - 版本管理 (版本检查、版本比较)

## 🔗 Session依赖关系

### 核心概念
在API测试中，**创建session是进行会话操作的前置条件**。所有需要session的测试都会自动创建session，确保测试的正确性。

### Session依赖的接口
以下接口需要先创建session才能正常测试：

1. **聊天相关接口**
   - `POST /api/gotgpt/chat` - AI聊天
   - `GET /api/godgpt/chat/{sessionId}` - 获取聊天历史
   - `DELETE /api/godgpt/chat/{sessionId}` - 删除会话
   - `GET /api/godgpt/session-info/{sessionId}` - 获取会话信息

2. **音频功能接口**
   - `POST /api/godgpt/voice/chat` - 语音聊天

3. **访客模式接口**
   - `POST /api/godgpt/guest/chat` - 访客聊天

### Session管理机制

#### 1. 自动Session创建
```python
@pytest.fixture
def create_session_fixture(self):
    """创建会话的fixture，供其他测试使用"""
    session_data = {
        "title": "Test Session for Chat",
        "type": "chat"
    }
    response = self.client.post("/godgpt/create-session", json=session_data)
    # 返回session_id供后续测试使用
    return response_data["data"]["sessionId"]
```

#### 2. 测试用例使用Session
```python
def test_chat_core_functionality(self, create_session_fixture):
    """测试AI聊天核心功能 - 需要先创建session"""
    chat_data = {
        "message": "Hello, how are you?",
        "sessionId": create_session_fixture,  # 使用创建的session
        "stream": True
    }
    response = self.client.post("/gotgpt/chat", json=chat_data)
```

#### 3. 全局Session管理器
```python
@pytest.fixture(scope="function")
def session_manager(api_client: APIClient):
    """会话管理器fixture，提供session的创建、管理和清理"""
    # 自动创建和管理session
    # 测试结束后自动清理
```

## 🚀 运行测试

### 1. 运行所有API测试
```bash
pytest tests/api_tests/
```

### 2. 按优先级运行测试
```bash
# 核心接口测试（包含session创建）
pytest tests/api_tests/ -m "core"

# 重要接口测试
pytest tests/api_tests/ -m "important"

# 功能接口测试
pytest tests/api_tests/ -m "functional"

# 系统接口测试
pytest tests/api_tests/ -m "system"
```

### 3. 按功能类型运行测试
```bash
# 冒烟测试（包含session创建）
pytest tests/api_tests/ -m "smoke"

# 安全测试
pytest tests/api_tests/ -m "security"

# 性能测试（包含session创建）
pytest tests/api_tests/ -m "performance"

# 集成测试（包含完整流程）
pytest tests/api_tests/ -m "integration"

# 回归测试
pytest tests/api_tests/ -m "regression"
```

### 4. 按关键词运行测试
```bash
# 聊天相关测试（自动创建session）
pytest tests/api_tests/ -k "chat"

# 支付相关测试
pytest tests/api_tests/ -k "payment"

# 会话相关测试（自动创建session）
pytest tests/api_tests/ -k "session"

# 用户相关测试
pytest tests/api_tests/ -k "user"
```

### 5. 生成测试报告
```bash
# HTML报告
pytest tests/api_tests/ --html=reports/api_test_report.html

# Allure报告
pytest tests/api_tests/ --alluredir=reports/allure

# 覆盖率报告
pytest tests/api_tests/ --cov=src --cov-report=html:reports/coverage
```

## 🔧 配置说明

### 环境变量配置
```bash
# API基础URL
API_BASE_URL=https://station-developer-staging.aevatar.ai/godgpt-client/api

# 测试项目ID
TEST_PROJECT_ID=4905508f-def5-ff31-f692-3a196ee1455d

# 认证配置 (必需)
AUTH_CLIENT_ID=your_client_id_here
AUTH_CLIENT_SECRET=your_client_secret_here

# 访问令牌 (可选，如果使用自动认证)
ACCESS_TOKEN=your_access_token

# 管理员令牌
ADMIN_TOKEN=your_admin_token

# 测试环境
TEST_ENV=staging
```

### 🔐 认证配置

#### 自动认证 (推荐)
框架支持自动认证，只需要设置客户端凭据：

```bash
# 设置认证凭据
export AUTH_CLIENT_ID="your_client_id"
export AUTH_CLIENT_SECRET="your_client_secret"

# 运行测试
python3 -m pytest tests/api_tests/test_core_apis.py -v
```

#### 手动认证
如果需要手动管理token：

```bash
# 获取token
curl --location 'https://auth-station-staging.aevatar.ai/connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode 'scope=Aevatar' \
--data-urlencode 'client_id=your_client_id' \
--data-urlencode 'client_secret=your_client_secret'

# 设置token
export ACCESS_TOKEN="your_access_token"
```

### 🔐 认证测试

#### **认证测试套件**
```bash
# 执行所有认证测试
python3 -m pytest tests/api_tests/test_auth_apis.py -v -s

# 执行特定认证测试
python3 -m pytest tests/api_tests/test_auth_apis.py::TestAuthAPIs::test_email_password_login -v -s
```

#### **认证测试覆盖范围**
- ✅ **核心认证接口 (6个)**
  - `POST /connect/token` - 邮箱密码登录
  - `POST /connect/token` - Google登录
  - `POST /connect/token` - Apple登录
  - `POST /api/account/check-email-registered` - 邮箱注册检查
  - `GET /api/account/logout` - 用户登出
  - `POST /api/account/send-verification-code` - 发送验证码
  - `POST /api/account/verify-code` - 验证验证码
  - `POST /api/account/reset-password` - 密码重置

- ✅ **认证流程接口 (3个)**
  - `GET /api/query/user-id` - 获取用户ID
  - `GET /api/godgpt/account` - 获取用户信息
  - 第三方OAuth流程 - Google/Apple授权

- ✅ **测试类型**
  - 功能测试
  - 安全测试 (SQL注入、暴力破解防护)
  - 性能测试 (响应时间验证)
  - 集成测试 (完整流程测试)
  - 错误处理 (异常情况处理)

#### **认证测试配置**
```yaml
# config/auth_test_data.yaml
auth_test_data:
  test_emails:
    valid_email: "test@example.com"
    invalid_email: "invalid_email"
  test_passwords:
    valid_password: "Test123456!"
    weak_password: "123"
  verification_codes:
    valid_code: "123456"
    invalid_code: "000000"
```

#### **认证测试工具**
```python
from utils.auth_test_utils import get_auth_test_utils

# 获取测试工具
auth_utils = get_auth_test_utils()

# 创建测试数据
login_data = auth_utils.create_email_password_login_data()
verification_data = auth_utils.create_verification_code_data()
```

### 测试数据配置
测试数据在 `tests/api_tests/conftest.py` 中的 `test_data` fixture中定义，包括：
- 用户测试数据
- 会话测试数据
- 支付测试数据
- 邀请测试数据
- 分享测试数据
- 音频测试数据
- 系统配置测试数据

## 📋 测试特性

### 1. 智能Session管理
- **自动创建**: 需要session的测试自动创建session
- **依赖注入**: 通过fixture注入session依赖
- **自动清理**: 测试结束后自动清理创建的session
- **错误处理**: session创建失败时的降级处理

### 2. 智能断言
- 统一的响应状态验证
- JSON响应格式验证
- 数据完整性检查
- 错误处理验证

### 3. 性能监控
- 响应时间监控
- 性能指标收集
- 超时控制

### 4. 安全测试
- 权限验证
- Token验证
- 数据安全测试

### 5. 数据驱动
- 参数化测试
- 边界条件测试
- 异常情况处理

### 6. 环境隔离
- 测试环境配置
- 数据清理机制
- 生产环境保护

## 📊 测试报告

### HTML报告
- 详细的测试结果
- 失败用例分析
- 执行时间统计
- 错误截图

### Allure报告
- 美观的界面
- 测试步骤详情
- 附件支持
- 趋势分析

### 覆盖率报告
- 代码覆盖率统计
- 未覆盖代码标识
- 覆盖率趋势

## 🔍 故障排除

### 常见问题

1. **Session创建失败**
   ```bash
   # 检查认证状态
   echo $ACCESS_TOKEN
   
   # 检查API连接
   curl -I $API_BASE_URL/godgpt/create-session
   
   # 查看详细错误
   pytest tests/api_tests/ -v -s -k "create_session"
   ```

2. **连接超时**
   ```bash
   # 检查网络连接
   curl -I $API_BASE_URL
   
   # 增加超时时间
   export PYTEST_TIMEOUT=30
   ```

3. **认证失败**
   ```bash
   # 检查Token有效性
   echo $ACCESS_TOKEN
   
   # 更新Token
   export ACCESS_TOKEN=new_token
   ```

4. **测试数据问题**
   ```bash
   # 清理测试数据
   pytest tests/api_tests/ --cleanup
   
   # 重置测试环境
   pytest tests/api_tests/ --reset-env
   ```

### 调试模式
```bash
# 启用详细日志
pytest tests/api_tests/ -v -s

# 只运行失败的测试
pytest tests/api_tests/ --lf

# 调试特定测试
pytest tests/api_tests/test_core_apis.py::TestCoreAPIs::test_chat_core_functionality -v -s

# 调试session创建
pytest tests/api_tests/test_core_apis.py::TestCoreAPIs::test_create_session -v -s
```

## 📈 持续集成

### GitHub Actions配置
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run API tests
        run: pytest tests/api_tests/ --html=reports/report.html
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: reports/
```

## 🤝 贡献指南

### 添加新测试
1. 确定测试优先级
2. 选择合适的测试文件
3. 如果测试需要session，使用session fixture
4. 添加测试用例
5. 更新文档

### 测试规范
- 使用描述性的测试名称
- 添加详细的测试步骤
- 包含正面和负面测试
- 添加适当的断言
- 需要session的测试必须使用session fixture

### 代码审查
- 检查测试覆盖率
- 验证测试逻辑
- 确保session依赖正确
- 确保代码质量
- 更新相关文档

## 📞 支持

如有问题或建议，请联系：
- 测试团队: test-team@example.com
- 技术文档: docs.example.com
- 问题反馈: github.com/example/api-automation/issues 