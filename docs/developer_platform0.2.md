# Plugin API 接口文档

## 接口概览

本API文档共包含4个接口，用于插件的管理操作：

1. **获取插件列表** (`GET /api/plugins`)
   - 获取指定项目下的所有插件列表

2. **新增插件** (`POST /api/plugins`)
   - 创建新的插件

3. **更新插件** (`PUT /api/plugins/{id}`)
   - 更新指定ID的插件内容

4. **删除插件** (`DELETE /api/plugins/{id}`)
   - 删除指定ID的插件

## 获取插件列表

### 请求信息
- **URL**: `/api/plugins`
- **Method**: `GET`
- **Header**: 
  - `Content-Type: application/json`
- **Parameters**:
  - `projectId`: string

### 响应信息
```json
{
  "code": "20000",
  "data": {
    "items": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "string",
        "creationTime": 0,
        "creatorName": ""
      }
    ]
  },
  "message": ""
}
```

## 新增插件

### 请求信息
- **URL**: `/api/plugins`
- **Method**: `POST`
- **Header**: 
  - `Content-Type: multipart/form-data`
- **Body**:
  - `projectId`: string
  - `code`: byte[]

### 响应信息
```json
{
  "code": "20000",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "displayName": "string",
    "memberCount": 0,
    "creationTime": 0
  },
  "message": ""
}
```

## 更新插件

### 请求信息
- **URL**: `/api/plugins/{id}`
- **Method**: `PUT`
- **Header**: 
  - `Content-Type: multipart/form-data`
- **Body**:
  - `code`: byte[]

### 响应信息
```json
{
  "code": "20000",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "string",
    "creationTime": 0,
    "creatorName": ""
  },
  "message": ""
}
```

## 删除插件

### 请求信息
- **URL**: `/api/plugins/{id}`
- **Method**: `DELETE`
- **Header**: 
  - `Content-Type: application/json`

### 响应信息
```json
{
  "code": "20001",
  "data": null,
  "message": ""
}
```