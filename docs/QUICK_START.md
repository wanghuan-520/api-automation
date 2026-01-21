# 快速开始指南

## 新项目使用框架

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```ini
# API配置
API_BASE_URL=https://your-api.example.com
API_TIMEOUT=30

# 认证配置（根据你的项目调整）
AUTH_TOKEN_URL=https://your-api.example.com/connect/token
TEST_USERNAME=your-username
TEST_PASSWORD=your-password
AUTH_CLIENT_ID=your-client-id
AUTH_SCOPE=your-scope

# 测试数据
TEST_PROJECT_ID=your-project-id
```

### 3. 创建业务适配器（可选）

如果你的项目有特定的业务逻辑（如编译、构建等），创建自定义适配器：

```python
# tests/adapters/myproject_adapter.py
from tests.adapters.base_adapter import BaseBusinessAdapter
from config.config_manager import ConfigManager

class MyProjectAdapter(BaseBusinessAdapter):
    def __init__(self, config: ConfigManager):
        super().__init__(config)
    
    def compile_artifact(self, artifact_id: str, **kwargs) -> bool:
        # 实现你的编译逻辑
        return True
    
    def get_artifact_path(self, artifact_id: str, **kwargs) -> str:
        # 返回构建产物路径
        return "/path/to/artifact"
    
    def upload_artifact(self, artifact_path: str, target_id: str, **kwargs) -> bool:
        # 实现上传逻辑
        return True
```

然后在 `tests/adapters/__init__.py` 中注册：

```python
def get_business_adapter() -> BaseBusinessAdapter:
    adapter_type = os.getenv('BUSINESS_ADAPTER_TYPE', 'myproject').lower()
    
    if adapter_type == 'myproject':
        return MyProjectAdapter(config)
    # ...
```

### 4. 编写测试用例

使用模板创建测试用例：

```python
# tests/test_my_api.py
import pytest
import allure
from tests.base_test import BaseAPITest

@allure.feature('我的API测试')
class TestMyAPI(BaseAPITest):
    @allure.story('获取资源')
    def test_get_resource(self):
        response = self.api_client.get('/api/resources')
        data = self.assert_success_response(response)
        self.assert_response_contains(response, ['items', 'total'])
```

### 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_my_api.py

# 生成报告
pytest --html=reports/report.html
```

---

## 从模板创建测试用例

1. 复制模板文件：
   ```bash
   cp tests/templates/test_api_template.py tests/test_my_api.py
   ```

2. 修改类名和测试用例：
   ```python
   class TestMyAPI(BaseAPITest):  # 修改类名
       def test_get_resource(self):  # 修改测试用例
           # 你的测试逻辑
   ```

3. 运行测试验证

---

## 配置验证

框架启动时会自动验证必要配置，如果配置缺失会给出提示：

```python
from config.config_manager import ConfigManager

config = ConfigManager()
is_valid, missing = config.validate_required(['base_url', 'auth.username'])

if not is_valid:
    print(f"缺少配置: {missing}")
```

---

## 更多信息

- 环境变量配置：`docs/ENV_SETUP.md`
- 框架评估：`docs/FRAMEWORK_EVALUATION.md`
- 改造总结：`docs/REFACTORING_SUMMARY.md`

