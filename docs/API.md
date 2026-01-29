# Aevatar Agent Framework API 接口文档

## 项目信息

- **项目名称**: Aevatar Agent Framework
- **技术栈**: C# ASP.NET Core
- **框架**: ABP Framework
- **文档生成时间**: 2024-01-22

---

## 目录

1. [状态查询模块 (State Query)](#1-状态查询模块-state-query)
2. [Agent演示模块 (Agent Demo)](#2-agent演示模块-agent-demo)

---

## 1. 状态查询模块 (State Query)

### 1.1 根据 ID 获取 Agent 状态

**接口描述：** 根据 Agent 类型和 ID 获取其当前状态。

**请求 URL：** `GET /api/states/{agentType}/{agentId}`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentType | string | path | 是 | Agent 类型名称 | 例如：`Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| agentId | string | path | 是 | Agent ID | UUID 格式 |

**请求示例：**
```bash
curl -X GET "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/123e4567-e89b-12d3-a456-426614174000" \
     -H "Accept: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.GetAsync(
    "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/123e4567-e89b-12d3-a456-426614174000");
var result = await response.Content.ReadFromJsonAsync<StateQueryResult>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/123e4567-e89b-12d3-a456-426614174000"
headers = {"Accept": "application/json"}
response = requests.get(url, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "123e4567-e89b-12d3-a456-426614174000",
  "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
  "data": {
    "message": "Hello from SimpleBusinessAgent"
  },
  "version": 1,
  "indexedAt": "2024-03-21T10:00:00Z"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 404 | 状态未找到 | 404 | 检查 Agent 类型和 ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 1.2 查询 Agent 状态（Lucene 查询）

**接口描述：** 使用 Lucene 查询语法查询 Agent 状态，支持分页。

**请求 URL：** `POST /api/states/query`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentType | string | body | 是 | Agent 类型名称 | 例如：`Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| queryString | string | body | 否 | Lucene 查询字符串 | 默认：`*`（查询所有） |
| pageIndex | int | body | 否 | 页码（从0开始） | 默认：0 |
| pageSize | int | body | 否 | 每页大小 | 默认：20，最大：100 |

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/states/query" \
     -H "Content-Type: application/json" \
     -d '{
       "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
       "queryString": "status:active AND version:>5",
       "pageIndex": 0,
       "pageSize": 20
     }'
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var request = new StateQuery
{
    AgentType = "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
    QueryString = "status:active AND version:>5",
    PageIndex = 0,
    PageSize = 20
};
var response = await client.PostAsJsonAsync("http://localhost:5000/api/states/query", request);
var result = await response.Content.ReadFromJsonAsync<PagedStateQueryResult>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/states/query"
headers = {"Content-Type": "application/json"}
data = {
    "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
    "queryString": "status:active AND version:>5",
    "pageIndex": 0,
    "pageSize": 20
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "totalCount": 50,
  "pageIndex": 0,
  "pageSize": 20,
  "items": [
    {
      "agentId": "123e4567-e89b-12d3-a456-426614174000",
      "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
      "data": {
        "status": "active",
        "version": 6
      },
      "version": 6,
      "indexedAt": "2024-03-21T10:00:00Z"
    }
  ]
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | 查询语法错误 | 400 | 检查 Lucene 查询语法是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 1.3 统计 Agent 状态数量

**接口描述：** 统计匹配查询条件的 Agent 状态数量。

**请求 URL：** `GET /api/states/{agentType}/count`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentType | string | path | 是 | Agent 类型名称 | 例如：`Aevatar.App.Agents.Agents.SimpleBusinessAgent` |
| queryString | string | query | 否 | Lucene 查询字符串 | 默认：`*`（统计所有） |

**请求示例：**
```bash
curl -X GET "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count?queryString=status:active" \
     -H "Accept: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.GetAsync(
    "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count?queryString=status:active");
var result = await response.Content.ReadFromJsonAsync<StateCountResponseDto>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/states/Aevatar.App.Agents.Agents.SimpleBusinessAgent/count"
params = {"queryString": "status:active"}
headers = {"Accept": "application/json"}
response = requests.get(url, params=params, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "agentType": "Aevatar.App.Agents.Agents.SimpleBusinessAgent",
  "count": 42
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | 查询语法错误 | 400 | 检查 Lucene 查询语法是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

## 2. Agent演示模块 (Agent Demo)

### 2.1 创建 Agent

**接口描述：** 创建一个新的 SimpleBusinessAgent 实例。

**请求 URL：** `POST /api/agent-demo/agents`

**权限要求：** 无

**请求参数：** 无

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/agents" \
     -H "Content-Type: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.PostAsync("http://localhost:5000/api/agent-demo/agents", null);
var result = await response.Content.ReadFromJsonAsync<AgentCreatedResponse>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/agents"
response = requests.post(url)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "Aevatar.App.Agents.Agents.SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "description": "SimpleBusinessAgent instance",
  "createdAt": "2024-03-21T10:00:00Z"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.2 发送消息给 Agent

**接口描述：** 向指定的 Agent 发送消息。

**请求 URL：** `POST /api/agent-demo/agents/{agentId}/messages`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentId | string | path | 是 | Agent ID | 支持原始 GUID 或完整 ActorId 格式 |
| message | string | body | 是 | 消息内容 | 非空字符串 |

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/messages" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, Agent!"
     }'
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var request = new AgentMessageRequest { Message = "Hello, Agent!" };
var response = await client.PostAsJsonAsync(
    "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/messages", 
    request);
var result = await response.Content.ReadFromJsonAsync<AgentMessageResponse>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/messages"
headers = {"Content-Type": "application/json"}
data = {"message": "Hello, Agent!"}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "Aevatar.App.Agents.Agents.SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "response": "Message processed successfully",
  "processedAt": "2024-03-21T10:00:00Z"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.3 获取 Agent 统计信息

**接口描述：** 获取指定 Agent 的统计信息。

**请求 URL：** `GET /api/agent-demo/agents/{agentId}/stats`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentId | string | path | 是 | Agent ID | 支持原始 GUID 或完整 ActorId 格式 |

**请求示例：**
```bash
curl -X GET "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/stats" \
     -H "Accept: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.GetAsync(
    "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/stats");
var result = await response.Content.ReadFromJsonAsync<AgentStatsResponse>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/stats"
headers = {"Accept": "application/json"}
response = requests.get(url, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "Aevatar.App.Agents.Agents.SimpleBusinessAgent:123e4567-e89b-12d3-a456-426614174000",
  "processedEventsCount": 5,
  "lastMessage": "Last processed message",
  "lastUpdated": "2024-03-21T10:00:00Z"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 404 | Agent 未找到 | 404 | 检查 Agent ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.4 设置 Agent 父子关系

**接口描述：** 建立 Agent 之间的父子关系（用于层次结构）。

**请求 URL：** `POST /api/agent-demo/agents/{childId}/parent/{parentId}`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| childId | string | path | 是 | 子 Agent ID | 支持原始 GUID 或完整 ActorId 格式 |
| parentId | string | path | 是 | 父 Agent ID | 支持原始 GUID 或完整 ActorId 格式 |

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/agents/child-agent-id/parent/parent-agent-id" \
     -H "Content-Type: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.PostAsync(
    "http://localhost:5000/api/agent-demo/agents/child-agent-id/parent/parent-agent-id", 
    null);
var result = await response.Content.ReadAsStringAsync();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/agents/child-agent-id/parent/parent-agent-id"
response = requests.post(url)
print(response.json())
```

**响应示例：**
```json
{
  "message": "Child child-agent-id now has parent parent-agent-id"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 404 | Agent 未找到 | 404 | 检查子 Agent 或父 Agent ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.5 发布事件到 Agent

**接口描述：** 向指定 Agent 的事件流发布事件。

**请求 URL：** `POST /api/agent-demo/agents/{agentId}/events`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentId | string | path | 是 | Agent ID | 支持原始 GUID 或完整 ActorId 格式 |
| message | string | body | 是 | 事件消息内容 | 非空字符串 |

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/events" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Event message"
     }'
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var request = new AgentEventRequest { Message = "Event message" };
var response = await client.PostAsJsonAsync(
    "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/events", 
    request);
var result = await response.Content.ReadAsStringAsync();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/agents/123e4567-e89b-12d3-a456-426614174000/events"
headers = {"Content-Type": "application/json"}
data = {"message": "Event message"}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "message": "Event published successfully",
  "eventData": "Event message"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 404 | Agent 未找到 | 404 | 检查 Agent ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.6 健康检查

**接口描述：** 检查 Agent 演示服务的健康状态。

**请求 URL：** `GET /api/agent-demo/health`

**权限要求：** 无

**请求参数：** 无

**请求示例：**
```bash
curl -X GET "http://localhost:5000/api/agent-demo/health"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.GetAsync("http://localhost:5000/api/agent-demo/health");
var result = await response.Content.ReadFromJsonAsync<object>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/health"
response = requests.get(url)
print(response.json())
```

**响应示例：**
```json
{
  "status": "Healthy",
  "timestamp": "2024-03-21T10:00:00Z"
}
```

---

### 2.7 创建复杂状态 Agent

**接口描述：** 创建一个 ComplexStateAgent 实例并初始化测试数据（用于测试 Elasticsearch 处理复杂类型）。

**请求 URL：** `POST /api/agent-demo/complex-agent`

**权限要求：** 无

**请求参数：** 无

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/complex-agent" \
     -H "Content-Type: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.PostAsync("http://localhost:5000/api/agent-demo/complex-agent", null);
var result = await response.Content.ReadFromJsonAsync<ComplexAgentCreatedResponse>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/complex-agent"
response = requests.post(url)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "Aevatar.App.Agents.Agents.ComplexStateAgent:123e4567-e89b-12d3-a456-426614174000",
  "description": "ComplexStateAgent with test data",
  "agentType": "Aevatar.App.Agents.Agents.ComplexStateAgent",
  "createdAt": "2024-03-21T10:00:00Z",
  "testDataInitialized": true
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.8 初始化复杂 Agent 测试数据

**接口描述：** 为已存在的 ComplexStateAgent 初始化测试数据（使用事件方式，兼容 Local 和 Orleans 模式）。

**请求 URL：** `POST /api/agent-demo/complex-agent/{agentId}/init`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentId | string | path | 是 | Agent ID | 支持原始 GUID 或完整 ActorId 格式 |

**请求示例：**
```bash
curl -X POST "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/init" \
     -H "Content-Type: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.PostAsync(
    "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/init", 
    null);
var result = await response.Content.ReadAsStringAsync();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/init"
response = requests.post(url)
print(response.json())
```

**响应示例：**
```json
{
  "message": "Test data initialized via event",
  "agentId": "Aevatar.App.Agents.Agents.ComplexStateAgent:123e4567-e89b-12d3-a456-426614174000"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 404 | Agent 未找到 | 404 | 检查 Agent ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

### 2.9 获取复杂 Agent 状态

**接口描述：** 获取 ComplexStateAgent 的状态（在 Orleans 模式下，完整状态应通过 `/api/states` 端点从 Elasticsearch 查询）。

**请求 URL：** `GET /api/agent-demo/complex-agent/{agentId}/state`

**权限要求：** 无

**请求参数：**
| 参数名 | 类型 | 位置 | 必填 | 描述 | 验证规则 |
|--------|------|------|------|------|----------|
| agentId | string | path | 是 | Agent ID | 支持原始 GUID 或完整 ActorId 格式 |

**请求示例：**
```bash
curl -X GET "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/state" \
     -H "Accept: application/json"
```

```csharp
// 使用HttpClient
using var client = new HttpClient();
var response = await client.GetAsync(
    "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/state");
var result = await response.Content.ReadFromJsonAsync<object>();
```

```python
# 使用requests
import requests

url = "http://localhost:5000/api/agent-demo/complex-agent/123e4567-e89b-12d3-a456-426614174000/state"
headers = {"Accept": "application/json"}
response = requests.get(url, headers=headers)
print(response.json())
```

**响应示例：**
```json
{
  "agentId": "Aevatar.App.Agents.Agents.ComplexStateAgent:123e4567-e89b-12d3-a456-426614174000",
  "description": "Agent description",
  "hint": "For full state in Orleans mode, use CQRS query: GET /api/states/Aevatar.App.Agents.Agents.ComplexStateAgent/123e4567-e89b-12d3-a456-426614174000"
}
```

**业务异常码：**
| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | Agent ID 格式无效 | 400 | 使用原始 GUID 或完整 ActorId 格式 |
| 404 | Agent 未找到 | 404 | 检查 Agent ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

## 数据模型定义

### StateQuery

查询请求模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentType | string | 是 | Agent 类型名称 |
| queryString | string | 否 | Lucene 查询字符串，默认：`*` |
| pageIndex | int | 否 | 页码（从0开始），默认：0 |
| pageSize | int | 否 | 每页大小，默认：20，最大：100 |

### StateQueryResult

状态查询结果模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentId | string | 是 | Agent ID |
| agentType | string | 是 | Agent 类型名称 |
| data | object | 否 | Agent 状态数据（字典类型） |
| version | int | 是 | 状态版本号 |
| indexedAt | DateTime | 否 | 索引时间 |

### PagedStateQueryResult

分页状态查询结果模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| totalCount | long | 是 | 总记录数 |
| pageIndex | int | 是 | 当前页码 |
| pageSize | int | 是 | 每页大小 |
| items | List<StateQueryResult> | 是 | 状态列表 |

### StateCountResponseDto

状态统计响应模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentType | string | 是 | Agent 类型名称 |
| count | long | 是 | 匹配的记录数 |

### AgentCreatedResponse

Agent 创建响应模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentId | string | 是 | Agent ID（完整 ActorId 格式） |
| description | string | 是 | Agent 描述 |
| createdAt | DateTime | 是 | 创建时间 |

### AgentMessageRequest

Agent 消息请求模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| message | string | 是 | 消息内容 |

### AgentMessageResponse

Agent 消息响应模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentId | string | 是 | Agent ID |
| response | string | 是 | Agent 响应内容 |
| processedAt | DateTime | 是 | 处理时间 |

### AgentStatsResponse

Agent 统计响应模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentId | string | 是 | Agent ID |
| processedEventsCount | int | 是 | 已处理事件数 |
| lastMessage | string | 是 | 最后一条消息 |
| lastUpdated | DateTime | 是 | 最后更新时间 |

### AgentEventRequest

Agent 事件请求模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| message | string | 是 | 事件消息内容 |

### ComplexAgentCreatedResponse

复杂 Agent 创建响应模型

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| agentId | string | 是 | Agent ID |
| description | string | 是 | Agent 描述 |
| agentType | string | 是 | Agent 类型名称 |
| createdAt | DateTime | 是 | 创建时间 |
| testDataInitialized | bool | 是 | 测试数据是否已初始化 |

---

## 通用错误码

| 错误码 | 说明 | HTTP状态码 | 解决方案 |
|--------|------|------------|----------|
| 400 | 请求参数错误 | 400 | 检查请求参数格式和必填项 |
| 404 | 资源未找到 | 404 | 检查资源 ID 是否正确 |
| 500 | 服务器内部错误 | 500 | 检查服务器日志，联系管理员 |

---

## 注意事项

1. **Agent ID 格式**：
   - 支持原始 GUID 格式：`123e4567-e89b-12d3-a456-426614174000`
   - 支持完整 ActorId 格式：`AgentType:123e4567-e89b-12d3-a456-426614174000`
   - 系统会自动规范化 ID 格式

2. **Lucene 查询语法**：
   - 支持标准 Lucene 查询语法
   - 示例：`status:active AND version:>5`
   - 默认查询所有：`*`

3. **Orleans 模式说明**：
   - 在 Orleans 模式下，Agent 运行在 Silo（Grain）中
   - 所有操作通过 Actor 代理转发到 Grain  via RPC
   - 完整状态查询应使用 CQRS 查询端点：`/api/states/{agentType}/{agentId}`

4. **事件处理**：
   - 使用事件方式初始化数据，兼容 Local 和 Orleans 模式
   - 事件通过 Actor 代理发布，在 Silo/Grain 中处理

5. **分页参数**：
   - `pageIndex` 从 0 开始
   - `pageSize` 最大值为 100
   - 默认 `pageSize` 为 20

---

**文档版本：** v1.0  
**最后更新：** 2024-01-22

