# 环境变量配置指南

## 概述

本框架使用环境变量管理敏感信息和配置，避免硬编码。配置优先级：**环境变量 > config.yaml > 默认值**

## 快速开始

### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件（已加入 `.gitignore`，不会被提交）：

```bash
cp .env.example .env  # 如果存在 .env.example
# 或手动创建 .env 文件
```

### 2. 配置环境变量

编辑 `.env` 文件，填写实际的配置值：

```ini
# API 配置
API_BASE_URL=https://aevatar-station-ui-staging.aevatar.ai/api/plugins
API_TIMEOUT=30
API_MAX_RETRIES=3

# 测试数据
TEST_PROJECT_ID=4905508f-def5-ff31-f692-3a196ee1455d

# 认证配置（重要：请勿提交到版本控制）
AUTH_TOKEN_URL=https://aevatar-station-ui-staging.aevatar.ai/connect/token
TEST_USERNAME=your-username@example.com
TEST_PASSWORD=your-password
AUTH_CLIENT_ID=AevatarAuthServer
AUTH_SCOPE=Aevatar offline_access
```

### 3. 验证配置

运行测试前，确保配置已正确加载：

```python
from config.config_manager import ConfigManager

config = ConfigManager()
print(config.get_all())  # 查看所有配置（密码会被掩码）
```

## 环境变量说明

### API 配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `API_BASE_URL` | API 基础 URL | `http://localhost:8000` | 是 |
| `API_TIMEOUT` | 请求超时时间（秒） | `30` | 否 |
| `API_MAX_RETRIES` | 最大重试次数 | `3` | 否 |

### 测试数据配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `TEST_PROJECT_ID` | 测试项目 ID | - | 是 |

### 认证配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `AUTH_TOKEN_URL` | 认证 Token URL | - | 是 |
| `TEST_USERNAME` | 测试用户名 | - | 是 |
| `TEST_PASSWORD` | 测试密码 | - | 是 |
| `AUTH_CLIENT_ID` | 认证客户端 ID | `AevatarAuthServer` | 否 |
| `AUTH_SCOPE` | 认证 Scope | - | 否（根据项目配置） |

### 业务适配器配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `BUSINESS_ADAPTER_TYPE` | 业务适配器类型（aevatar/通用） | `aevatar` | 否 |
| `DLL_BUILD_PATH` | DLL构建路径（Aevatar适配器使用） | - | 否（如使用DLL编译功能） |
| `DLL_PROJECT_NAME` | DLL项目名称 | `TestGAgent` | 否 |

### 环境配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `TEST_ENV` | 测试环境（dev/test/staging） | `test` | 否 |

## 多环境配置

### 方式一：使用环境变量（推荐）

```bash
# 开发环境
export TEST_ENV=dev
export API_BASE_URL=http://dev-api.example.com
export TEST_USERNAME=dev-user@example.com
export TEST_PASSWORD=dev-password

# 测试环境
export TEST_ENV=test
export API_BASE_URL=https://test-api.example.com
export TEST_USERNAME=test-user@example.com
export TEST_PASSWORD=test-password
```

### 方式二：使用 config.yaml

编辑 `config/config.yaml`：

```yaml
env:
  dev:
    base_url: "http://dev-api.example.com"
    timeout: 30
    test_project_id: "dev-project-id"
  test:
    base_url: "https://test-api.example.com"
    timeout: 30
    test_project_id: "test-project-id"
  staging:
    base_url: "https://staging-api.example.com"
    timeout: 30
    test_project_id: "staging-project-id"
```

然后通过环境变量切换：

```bash
export TEST_ENV=dev  # 或 test、staging
pytest
```

## 安全注意事项

### ✅ 正确做法

1. **使用 .env 文件**（已加入 .gitignore）
   ```bash
   # .env
   TEST_PASSWORD=your-password
   ```

2. **使用环境变量**
   ```bash
   export TEST_PASSWORD=your-password
   pytest
   ```

3. **使用密钥管理服务**（生产环境推荐）
   ```python
   # 从 AWS Secrets Manager、Azure Key Vault 等获取
   password = get_secret_from_vault('test_password')
   ```

### ❌ 错误做法

1. **硬编码在代码中**
   ```python
   # ❌ 不要这样做
   password = 'Wh520520!'
   ```

2. **提交 .env 文件到版本控制**
   ```bash
   # ❌ 不要这样做
   git add .env
   git commit -m "add config"
   ```

3. **在日志中输出敏感信息**
   ```python
   # ❌ 不要这样做
   logger.info(f"Password: {password}")
   ```

## 配置验证

### 检查配置是否加载

```python
from config.config_manager import ConfigManager

config = ConfigManager()

# 检查必要配置
required_configs = ['base_url', 'auth.username', 'auth.password']
missing = [key for key in required_configs if not config.get(key)]

if missing:
    print(f"缺少必要配置: {missing}")
    print("请检查 .env 文件或环境变量")
else:
    print("配置加载成功")
    print(config.get_all())  # 查看所有配置（密码会被掩码）
```

### 运行配置检查脚本

```bash
python -c "from config.config_manager import ConfigManager; c = ConfigManager(); print('✓ 配置加载成功' if c.get('base_url') else '✗ 配置加载失败')"
```

## 常见问题

### Q1: 配置未生效？

**A:** 检查以下几点：
1. `.env` 文件是否在项目根目录
2. 是否安装了 `python-dotenv`：`pip install python-dotenv`
3. 环境变量名称是否正确（区分大小写）

### Q2: 如何在不同环境间切换？

**A:** 使用 `TEST_ENV` 环境变量：
```bash
export TEST_ENV=dev && pytest
export TEST_ENV=staging && pytest
```

### Q3: 密码被提交到版本控制怎么办？

**A:** 立即：
1. 修改密码
2. 从 Git 历史中删除敏感信息：
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. 强制推送（谨慎操作）

### Q4: 团队如何共享配置？

**A:** 
1. 创建 `.env.example` 模板（不含敏感信息）
2. 在文档中说明如何配置
3. 使用密钥管理服务（生产环境）

## 参考

- [python-dotenv 文档](https://github.com/theskumar/python-dotenv)
- [12-Factor App: Config](https://12factor.net/config)
- [OWASP: Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_cryptographic_key)

