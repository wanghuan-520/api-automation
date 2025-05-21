# GodGPT API 接口文档

## 接口概览

本API文档共包含7个接口，用于GodGPT的对话和账户管理：

1. **发起对话** (`POST /api/godgpt/chat`)
   - 创建新的对话流

2. **查询用户信息** (`GET /api/godgpt/account`)
   - 获取当前登录用户的Profile信息

3. **更新Credits Toast展示状态** (`POST /api/godgpt/account/show-toast`)
   - 更新Credits Toast为已展示状态

4. **查询Stripe公钥** (`GET /api/godgpt/payment/keys`)
   - 获取支付系统的公钥信息

5. **查询商品及价格** (`GET /api/godgpt/payment/products`)
   - 获取可购买的商品和价格信息

6. **创建支付Session** (`POST /api/godgpt/payment/create-checkout-session`)
   - 创建新的支付会话

7. **查询支付列表** (`GET /api/godgpt/payment/list`)
   - 获取用户的支付记录

## 发起对话

### 请求信息
- **URL**: `/api/godgpt/chat`
- **Method**: `POST`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是
- **Body**:
```json
{
    "sessionId": "string",
    "content": "string",
    "region": "" //CN
}
```

### HTTP状态码
- 402: Your credits are used up
- 429: You've reached the message limit of 25/40 in 3 hours. Please wait and try again later.
- 500: Internal Server Error

### 响应信息
```json
{
    "code": "20000",
    "data": {
        "content": "string",
        "newTitle": "string"
    },
    "message": ""
}
```

## 查询用户信息

### 请求信息
- **URL**: `/api/godgpt/account`
- **Method**: `GET`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是

### 响应信息
```json
{
    "code": "20000",
    "data": {
        "gender": "string",
        "birthDate": "Datetime",
        "birthPlace": "string",
        "fullName": "string",
        "credits": {
            "isInitialized": "bool",
            "credits": "int", //剩余credits数量
            "shouldShowToast": "bool" //是否需要展示credits提示
        }, 
        "subscription": {
            "isActive": "bool", //是否订阅用户
            "planType": "enum", //Day=1,Month=2,Year=3
            "startDate": "DateTime", //订阅开始时间
            "endDate": "DateTime" //订阅结束时间
        }
    },
    "message": ""
}
```

## 更新Credits Toast展示状态

### 请求信息
- **URL**: `/api/godgpt/account/show-toast`
- **Method**: `POST`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是
- **Body**:
```json
{
}
```

### 响应信息
```json
{
    "code": "20000",
    "data": "string", //已完成展示状态更新的userId
    "message": ""
}
```

## 查询Stripe公钥

### 请求信息
- **URL**: `/api/godgpt/payment/keys`
- **Method**: `GET`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是

### 响应信息
```json
{
    "code": "20000",
    "data": {
        "publishableKey": "string"  
    },
    "message": ""
}
```

## 查询商品及价格

### 请求信息
- **URL**: `/api/godgpt/payment/products`
- **Method**: `GET`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是

### 响应信息
```json
{
    "code": "20000",
    "data": {
        "planType": "enum", //Day = 1, Month = 2, Year = 3   
        "priceId": "string",
        "mode": "string",
        "amount": "decimal",
        "dailyAvgPrice": "string", //每天平均价格       
        "currency": "string"
    },
    "message": ""
}
```

## 创建支付Session

### 请求信息
- **URL**: `/api/godgpt/payment/create-checkout-session`
- **Method**: `POST`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是
- **Body**:
```json
{
    "priceId": "string",
    "mode": "subscription",
    "quantity": 1
}
```

### 响应信息
重定向到stripe付款页

## 查询支付列表

### 请求信息
- **URL**: `/api/godgpt/payment/list`
- **Method**: `GET`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是

### 响应信息
```json
{
    "code": "20000",
    "data": [
        {
            "paymentGrainId": "6828cf38-e27e-4583-b23b-6799e94d47c1",
            "orderId": null,
            "planType": 1,
            "amount": 0.0,
            "currency": "USD",
            "createdAt": "2025-05-20T00:52:45.504766Z",
            "completedAt": "2025-05-20T00:52:45.501398Z",
            "status": 3,
            "paymentType": 0,
            "method": 0,
            "platform": 0,
            "isSubscriptionRenewal": true,
            "subscriptionId": null,
            "subscriptionStartDate": "0001-01-01T00:00:00",
            "subscriptionEndDate": "0001-01-01T00:00:00",
            "sessionId": null
        }
    ],
    "message": ""
}
```

## 支付回调接口

### 请求信息
- **URL**: `/api/godgpt/payment/webhook`
- **Method**: `POST`
- **Header**: 
  - `Content-Type: application/json`
- **是否需要登录**: 是

### 响应信息
无响应内容