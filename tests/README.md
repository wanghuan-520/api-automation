# API自动化测试脚本使用说明

## 概述

本目录包含基于pytest + allure的API自动化测试脚本，测试用例数据来自 `test-cases/all_api_test_cases.csv`。

## 测试文件结构

- `test_state_query.py`: 状态查询模块测试（TC01开头）
- `test_agent_demo.py`: Agent演示模块测试（TC02开头）

## 运行测试

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export API_BASE_URL=http://localhost:5000
```

### 3. 运行所有测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_state_query.py
pytest tests/test_agent_demo.py

# 运行特定测试类型
pytest -m positive    # 正向测试
pytest -m negative   # 负向测试
pytest -m boundary   # 边界测试

# 运行特定优先级
pytest -m high       # 高优先级
pytest -m medium     # 中优先级
pytest -m low        # 低优先级
```

### 4. 生成测试报告

```bash
# 运行测试并生成allure报告
pytest --alluredir=allure-results

# 查看allure报告
allure serve allure-results

# 生成HTML报告（自动生成到reports/report.html）
pytest
```

## 测试用例数据

测试用例数据存储在 `test-cases/all_api_test_cases.csv`，包含以下字段：

- `test_case_id`: 测试用例ID（格式：TC{模块}{接口}{用例}）
- `test_case_name`: 测试用例名称
- `api_name`: 接口名称
- `method`: HTTP方法
- `url`: 请求URL
- `headers`: 请求头（JSON格式）
- `request_data`: 请求参数（JSON格式）
- `expected_status_code`: 期望状态码
- `expected_response`: 期望响应（JSON格式）
- `test_type`: 测试类型（positive/negative/boundary）
- `priority`: 优先级（high/medium/low）
- `description`: 测试描述
- `tags`: 标签（逗号分隔）

## 测试执行流程

1. **数据加载**: 从CSV文件加载测试用例数据
2. **参数化**: 使用pytest参数化将CSV数据转换为测试参数
3. **请求发送**: 根据测试用例数据发送HTTP请求
4. **响应验证**: 验证状态码和响应内容
5. **报告生成**: 生成allure和HTML测试报告

## 注意事项

1. 确保API服务已启动并可通过 `API_BASE_URL` 访问
2. 测试用例中的URL是相对路径，会自动拼接 `API_BASE_URL`
3. 期望响应验证采用宽松模式，只验证关键字段
4. 对于空字符串的期望值，会跳过验证

## 故障排查

### 问题：测试用例未执行

- 检查CSV文件路径是否正确
- 检查CSV文件编码是否为UTF-8
- 检查测试用例ID格式是否正确

### 问题：请求失败

- 检查 `API_BASE_URL` 环境变量是否正确设置
- 检查API服务是否正常运行
- 检查网络连接

### 问题：断言失败

- 检查期望响应数据是否正确
- 检查API响应格式是否与期望一致
- 查看allure报告中的详细响应信息

