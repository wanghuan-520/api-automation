# Aevatar Agent Framework API 接口测试文档

## 接口概览

本文档包含 Aevatar Agent Framework 后端 API 的完整接口测试文档，共包含 **3个主要模块**：

1. **状态查询模块** (`/api/states`) - 3个接口
   - 用于查询和统计 Agent 状态（基于 Elasticsearch CQRS 读模型）

2. **Agent 演示模块** (`/api/agent-demo`) - 10个接口
   - 用于创建、管理和测试 Agent 功能

3. **Secrets 配置模块** (`/api/*`) - 本地配置 API
   - 用于管理 LLM 提供商配置和加密密钥（仅限 localhost）

---

## 1. 状态查询模块 (State Query)

### 1.1 根据 ID 获取 Agent 状态

**接口描述：** 根据 Agent 类型和 ID 获取单个 Agent 的状态信息

**请求 URL：** `GET /api/states/{agentType}/{agentId}`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentType | string | path | 是 | Agent 类型名称 | `Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| agentId | string | path | 是 | Agent ID（支持 raw Guid 或完整 ActorId） | `123e4567-e89b-12d3-a456-426614174000` |

**请求示例：**

```bash
# 使用 curl
curl -X GET "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/123e4567-e89b-12d3-a456-426614174000"
```

```python
# 使用 Python requests
import requests

response = requests.get(
    "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/123e4567-e89b-12d3-a456-426614174000"
)
print(response.json())
```

**响应示例：**

```json
{
  "agentId": "123e4567-e89b-12d3-a456-426614174000",
  "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
  "data": {
    "message": "Hello World",
    "processedCount": 5
  },
  "version": 1,
  "indexedAt": "2024-01-01T12:00:00Z"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 404 | Agent 状态未找到 | `{"error": "State not found for agent {agentType}/{agentId}"}` |
| 500 | 服务器内部错误 | `{"error": "Error message"}` |

**测试用例：**

```python
def test_get_state_by_id_success():
    """测试成功获取状态"""
    response = api_client.get(
        "/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/test-agent-id"
    )
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert "agentType" in response.json()
    assert "data" in response.json()

def test_get_state_by_id_not_found():
    """测试不存在的 Agent ID"""
    response = api_client.get(
        "/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/non-existent-id"
    )
    assert response.status_code == 404
```

---

### 1.2 查询 Agent 状态（Lucene 查询）

**接口描述：** 使用 Lucene 查询语法查询 Agent 状态，支持分页和排序

**请求 URL：** `POST /api/states/query`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| AgentType | string | body | 是 | Agent 类型名称 | `Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| QueryString | string | body | 否 | Lucene 查询字符串，默认为 `*` | `username:alice* AND isActive:true` |
| PageIndex | int | body | 否 | 页码（0-based），默认 0 | `0` |
| PageSize | int | body | 否 | 每页大小，默认 20 | `20` |
| SortFields | array | body | 否 | 排序字段列表 | `["fieldName:asc", "fieldName:desc"]` |

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/states/query" \
  -H "Content-Type: application/json" \
  -d '{
    "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
    "queryString": "message:Hello*",
    "pageIndex": 0,
    "pageSize": 20,
    "sortFields": ["indexedAt:desc"]
  }'
```

```python
# 使用 Python requests
import requests

response = requests.post(
    "http://localhost:5000/api/states/query",
    json={
        "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
        "queryString": "message:Hello*",
        "pageIndex": 0,
        "pageSize": 20,
        "sortFields": ["indexedAt:desc"]
    }
)
print(response.json())
```

**响应示例：**

```json
{
  "totalCount": 100,
  "items": [
    {
      "agentId": "123e4567-e89b-12d3-a456-426614174000",
      "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
      "data": {
        "message": "Hello World"
      },
      "version": 1,
      "indexedAt": "2024-01-01T12:00:00Z"
    }
  ],
  "pageIndex": 0,
  "pageSize": 20,
  "totalPages": 5
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 500 | 服务器内部错误 | `{"error": "Error message"}` |

**测试用例：**

```python
def test_query_states_success():
    """测试成功查询状态"""
    response = api_client.post(
        "/api/states/query",
        json={
            "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
            "queryString": "*",
            "pageIndex": 0,
            "pageSize": 10
        }
    )
    assert response.status_code == 200
    assert "totalCount" in response.json()
    assert "items" in response.json()
    assert isinstance(response.json()["items"], list)

def test_query_states_with_lucene_query():
    """测试使用 Lucene 查询语法"""
    response = api_client.post(
        "/api/states/query",
        json={
            "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
            "queryString": "message:Hello* AND processedCount:[5 TO 10]",
            "pageIndex": 0,
            "pageSize": 20
        }
    )
    assert response.status_code == 200
```

---

### 1.3 统计 Agent 状态数量

**接口描述：** 统计指定 Agent 类型的状态数量，支持可选的 Lucene 查询过滤

**请求 URL：** `GET /api/states/{agentType}/count`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentType | string | path | 是 | Agent 类型名称 | `Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| queryString | string | query | 否 | Lucene 查询字符串，默认为 `*` | `message:Hello*` |

**请求示例：**

```bash
# 使用 curl
curl -X GET "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count?queryString=message:Hello*"
```

```python
# 使用 Python requests
import requests

response = requests.get(
    "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count",
    params={"queryString": "message:Hello*"}
)
print(response.json())
```

**响应示例：**

```json
{
  "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
  "count": 100
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 500 | 服务器内部错误 | `{"error": "Error message"}` |

**测试用例：**

```python
def test_count_states_success():
    """测试成功统计状态数量"""
    response = api_client.get(
        "/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count"
    )
    assert response.status_code == 200
    assert "agentType" in response.json()
    assert "count" in response.json()
    assert isinstance(response.json()["count"], int)

def test_count_states_with_query():
    """测试使用查询条件统计"""
    response = api_client.get(
        "/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count",
        params={"queryString": "message:Hello*"}
    )
    assert response.status_code == 200
    assert response.json()["count"] >= 0
```

---

## 2. Agent 演示模块 (Agent Demo)

### 2.1 创建 Agent

**接口描述：** 创建一个新的 SimpleBusinessAgent 实例

**请求 URL：** `POST /api/agent-demo/agents`

**权限要求：** 无

**请求参数：** 无

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/agents"
```

```python
# 使用 Python requests
import requests

response = requests.post("http://localhost:5000/api/agent-demo/agents")
print(response.json())
```

**响应示例：**

```json
{
  "agentId": "SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "description": "Agent description",
  "createdAt": "2024-01-01T12:00:00Z"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_create_agent_success():
    """测试成功创建 Agent"""
    response = api_client.post("/api/agent-demo/agents")
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert "description" in response.json()
    assert "createdAt" in response.json()
```

---

### 2.2 发送消息给 Agent

**接口描述：** 向指定 Agent 发送消息，Agent 会处理消息并返回更新后的描述

**请求 URL：** `POST /api/agent-demo/agents/{agentId}/messages`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentId | string | path | 是 | Agent ID（支持 raw Guid 或完整 ActorId） | `123e4567-e89b-12d3-a456-426614174000` |
| Message | string | body | 是 | 要发送的消息内容 | `"Hello, Agent!"` |

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, Agent!"
  }'
```

```python
# 使用 Python requests
import requests

response = requests.post(
    "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/messages",
    json={"message": "Hello, Agent!"}
)
print(response.json())
```

**响应示例：**

```json
{
  "agentId": "SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "response": "Agent processed message: Hello, Agent!",
  "processedAt": "2024-01-01T12:00:00Z"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid agent ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_send_message_success():
    """测试成功发送消息"""
    # 先创建 Agent
    create_response = api_client.post("/api/agent-demo/agents")
    agent_id = create_response.json()["agentId"]
    
    # 发送消息
    response = api_client.post(
        f"/api/agent-demo/agents/{agent_id}/messages",
        json={"message": "Test message"}
    )
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert "response" in response.json()

def test_send_message_invalid_id():
    """测试无效的 Agent ID"""
    response = api_client.post(
        "/api/agent-demo/agents/invalid-id/messages",
        json={"message": "Test"}
    )
    assert response.status_code == 400
```

---

### 2.3 获取 Agent 统计信息

**接口描述：** 获取指定 Agent 的统计信息

**请求 URL：** `GET /api/agent-demo/agents/{agentId}/stats`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentId | string | path | 是 | Agent ID（支持 raw Guid 或完整 ActorId） | `123e4567-e89b-12d3-a456-426614174000` |

**请求示例：**

```bash
# 使用 curl
curl -X GET "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/stats"
```

**响应示例：**

```json
{
  "agentId": "SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "processedEventsCount": 5,
  "lastMessage": "Agent description",
  "lastUpdated": "2024-01-01T12:00:00Z"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid agent ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 404 | Agent 不存在 | `"Agent {agentId} not found"` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_get_stats_success():
    """测试成功获取统计信息"""
    # 先创建 Agent
    create_response = api_client.post("/api/agent-demo/agents")
    agent_id = create_response.json()["agentId"]
    
    response = api_client.get(f"/api/agent-demo/agents/{agent_id}/stats")
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert "processedEventsCount" in response.json()
```

---

### 2.4 设置 Agent 父子关系

**接口描述：** 建立 Agent 之间的父子关系（用于层次结构）

**请求 URL：** `POST /api/agent-demo/agents/{childId}/parent/{parentId}`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| childId | string | path | 是 | 子 Agent ID | `123e4567-e89b-12d3-a456-426614174000` |
| parentId | string | path | 是 | 父 Agent ID | `223e4567-e89b-12d3-a456-426614174001` |

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/agents/child-id/parent/parent-id"
```

**响应示例：**

```json
{
  "message": "Child SimpleBusinessAgent:child-id now has parent SimpleBusinessAgent:parent-id"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 404 | Agent 不存在 | `"Child agent {childId} not found"` 或 `"Parent agent {parentId} not found"` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_set_parent_success():
    """测试成功设置父子关系"""
    # 创建父 Agent
    parent_response = api_client.post("/api/agent-demo/agents")
    parent_id = parent_response.json()["agentId"]
    
    # 创建子 Agent
    child_response = api_client.post("/api/agent-demo/agents")
    child_id = child_response.json()["agentId"]
    
    # 设置父子关系
    response = api_client.post(
        f"/api/agent-demo/agents/{child_id}/parent/{parent_id}"
    )
    assert response.status_code == 200
    assert "message" in response.json()
```

---

### 2.5 发布事件到 Agent

**接口描述：** 向指定 Agent 发布事件

**请求 URL：** `POST /api/agent-demo/agents/{agentId}/events`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentId | string | path | 是 | Agent ID | `123e4567-e89b-12d3-a456-426614174000` |
| Message | string | body | 是 | 事件消息内容 | `"Event message"` |

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/agents/agent-id/events" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Event message"
  }'
```

**响应示例：**

```json
{
  "message": "Event published successfully",
  "eventData": "Event message"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid agent ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 404 | Agent 不存在 | `"Agent {agentId} not found"` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_publish_event_success():
    """测试成功发布事件"""
    # 创建 Agent
    create_response = api_client.post("/api/agent-demo/agents")
    agent_id = create_response.json()["agentId"]
    
    response = api_client.post(
        f"/api/agent-demo/agents/{agent_id}/events",
        json={"message": "Test event"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
```

---

### 2.6 健康检查

**接口描述：** 检查 Agent Demo 服务的健康状态

**请求 URL：** `GET /api/agent-demo/health`

**权限要求：** 无

**请求参数：** 无

**请求示例：**

```bash
# 使用 curl
curl -X GET "http://localhost:5000/api/agent-demo/health"
```

**响应示例：**

```json
{
  "status": "Healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**测试用例：**

```python
def test_health_check():
    """测试健康检查"""
    response = api_client.get("/api/agent-demo/health")
    assert response.status_code == 200
    assert response.json()["status"] == "Healthy"
```

---

### 2.7 创建复杂状态 Agent

**接口描述：** 创建一个 ComplexStateAgent 实例，用于测试 Elasticsearch 处理复杂类型（List、Dict、嵌套对象）

**请求 URL：** `POST /api/agent-demo/complex-agent`

**权限要求：** 无

**请求参数：** 无

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/complex-agent"
```

**响应示例：**

```json
{
  "agentId": "ComplexStateAgent:123e4567-e89b-12d3-a456-426614174000",
  "description": "Agent description",
  "agentType": "Aevatar.App.Agents.Agents.ComplexStateAgent",
  "createdAt": "2024-01-01T12:00:00Z",
  "testDataInitialized": true
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_create_complex_agent_success():
    """测试成功创建复杂状态 Agent"""
    response = api_client.post("/api/agent-demo/complex-agent")
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert response.json()["testDataInitialized"] == True
```

---

### 2.8 初始化复杂 Agent 测试数据

**接口描述：** 为已存在的复杂 Agent 初始化测试数据（使用事件方式，兼容 Local 和 Orleans 模式）

**请求 URL：** `POST /api/agent-demo/complex-agent/{agentId}/init`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentId | string | path | 是 | Agent ID | `123e4567-e89b-12d3-a456-426614174000` |

**请求示例：**

```bash
# 使用 curl
curl -X POST "http://localhost:5000/api/agent-demo/complex-agent/agent-id/init"
```

**响应示例：**

```json
{
  "message": "Test data initialized via event",
  "agentId": "ComplexStateAgent:agent-id"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid agent ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 404 | Agent 不存在 | `"Agent {agentId} not found"` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_init_complex_agent_data():
    """测试初始化复杂 Agent 测试数据"""
    # 先创建复杂 Agent
    create_response = api_client.post("/api/agent-demo/complex-agent")
    agent_id = create_response.json()["agentId"]
    
    response = api_client.post(f"/api/agent-demo/complex-agent/{agent_id}/init")
    assert response.status_code == 200
    assert "message" in response.json()
```

---

### 2.9 获取复杂 Agent 状态

**接口描述：** 获取复杂 Agent 的状态信息。注意：在 Orleans 模式下，完整状态应通过 CQRS 查询端点 `/api/states/{agentType}/{agentId}` 获取

**请求 URL：** `GET /api/agent-demo/complex-agent/{agentId}/state`

**权限要求：** 无

**请求参数：**

| 参数名 | 类型 | 位置 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|------|
| agentId | string | path | 是 | Agent ID | `123e4567-e89b-12d3-a456-426614174000` |

**请求示例：**

```bash
# 使用 curl
curl -X GET "http://localhost:5000/api/agent-demo/complex-agent/agent-id/state"
```

**响应示例：**

```json
{
  "agentId": "ComplexStateAgent:agent-id",
  "description": "Agent description",
  "hint": "For full state in Orleans mode, use CQRS query: GET /api/states/Aevatar.App.Agents.Agents.ComplexStateAgent/{agentId}"
}
```

**错误响应：**

| HTTP状态码 | 说明 | 响应示例 |
|------------|------|----------|
| 400 | Agent ID 格式无效 | `"Invalid agent ID format. Use raw Guid or full ActorId (AgentType:Guid)."` |
| 404 | Agent 不存在 | `"Agent {agentId} not found"` |
| 500 | 服务器内部错误 | `"Error: Error message"` |

**测试用例：**

```python
def test_get_complex_agent_state():
    """测试获取复杂 Agent 状态"""
    # 先创建复杂 Agent
    create_response = api_client.post("/api/agent-demo/complex-agent")
    agent_id = create_response.json()["agentId"]
    
    response = api_client.get(f"/api/agent-demo/complex-agent/{agent_id}/state")
    assert response.status_code == 200
    assert "agentId" in response.json()
    assert "hint" in response.json()
```

---

## 3. 业务异常码

### 3.1 通用错误码

| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | 请求参数错误 | 400 | 检查请求参数格式和必填项 |
| 404 | 资源不存在 | 404 | 确认资源 ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 查看服务器日志，联系技术支持 |

### 3.2 Agent 相关错误

| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用 raw Guid 或完整 ActorId (AgentType:Guid) 格式 |
| 404 | Agent 不存在 | 404 | 确认 Agent 已创建，或先调用创建接口 |

### 3.3 状态查询相关错误

| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 404 | 状态未找到 | 404 | 确认 Agent 已创建并已索引到 Elasticsearch |
| 500 | 查询执行失败 | 500 | 检查 Elasticsearch 连接和查询语法 |

---

## 4. 测试用例设计建议

### 4.1 状态查询模块测试

1. **基础功能测试**
   - 测试根据 ID 获取状态（存在/不存在）
   - 测试 Lucene 查询（简单查询/复杂查询/分页/排序）
   - 测试统计功能（全部统计/条件统计）

2. **边界条件测试**
   - 测试空查询结果
   - 测试超大分页参数
   - 测试无效的 Lucene 查询语法

3. **性能测试**
   - 测试大量数据查询性能
   - 测试复杂查询性能

### 4.2 Agent 演示模块测试

1. **Agent 生命周期测试**
   - 创建 Agent → 发送消息 → 获取统计 → 发布事件
   - 测试 Agent 父子关系建立
   - 测试复杂状态 Agent 的创建和初始化

2. **错误处理测试**
   - 测试无效 Agent ID 格式
   - 测试不存在的 Agent 操作
   - 测试消息发送失败场景

3. **集成测试**
   - 测试 Agent 创建后状态查询
   - 测试事件发布后状态更新
   - 测试 Orleans 模式下的状态查询

### 4.3 测试数据准备

```python
# 测试数据示例
TEST_AGENT_TYPE = "Aevatar.App.Agents.Agents.SimpleBusinessAgent"
TEST_COMPLEX_AGENT_TYPE = "Aevatar.App.Agents.Agents.ComplexStateAgent"

# 创建测试 Agent
def create_test_agent():
    response = api_client.post("/api/agent-demo/agents")
    return response.json()["agentId"]

# 创建测试复杂 Agent
def create_test_complex_agent():
    response = api_client.post("/api/agent-demo/complex-agent")
    return response.json()["agentId"]
```

---

## 5. 使用说明

### 5.1 环境配置

```bash
# 设置 API 基础 URL
export API_BASE_URL=http://localhost:5000

# 或使用配置文件
# config/config.yaml
api:
  base_url: http://localhost:5000
```

### 5.2 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块测试
pytest tests/agent_demo/

# 运行特定接口测试
pytest tests/agent_demo/test_agent_creation.py
```

### 5.3 注意事项

1. **Agent ID 格式**
   - 支持 raw Guid: `123e4567-e89b-12d3-a456-426614174000`
   - 支持完整 ActorId: `SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000`

2. **Orleans 模式**
   - 在 Orleans 模式下，Agent 运行在 Silo (Grain) 中
   - 完整状态需要通过 CQRS 查询端点获取

3. **状态查询**
   - 状态查询基于 Elasticsearch CQRS 读模型
   - 支持 Lucene 查询语法
   - 状态更新可能有延迟（最终一致性）

4. **本地配置 API**
   - Secrets API 仅限 localhost 访问
   - 用于管理 LLM 提供商配置和加密密钥

---

## 6. 附录

### 6.1 数据模型定义

#### StateQuery
```json
{
  "agentType": "string",
  "queryString": "string?",
  "pageIndex": 0,
  "pageSize": 20,
  "sortFields": ["string"]
}
```

#### StateQueryResult
```json
{
  "agentId": "string",
  "agentType": "string",
  "data": {},
  "version": 0,
  "indexedAt": "datetime?"
}
```

#### PagedStateQueryResult
```json
{
  "totalCount": 0,
  "items": [],
  "pageIndex": 0,
  "pageSize": 20,
  "totalPages": 0
}
```

### 6.2 参考文档

- [ABP Framework 文档](https://docs.abp.io/)
- [Orleans 文档](https://dotnet.github.io/orleans/)
- [Elasticsearch 查询语法](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html)

---

**文档版本：** v1.0  
**生成时间：** 2024-01-01  
**适用范围：** Aevatar Agent Framework 后端 API 测试  
**支持框架：** ASP.NET Core, ABP Framework, Orleans

