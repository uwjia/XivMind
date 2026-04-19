# XivMind API Tester

独立的 API 测试系统，用于测试 XivMind 项目的所有接口。

## 功能特性

- 自动加载 XivMind 项目的所有 API 接口
- 按模块分组展示接口
- 支持 GET、POST、PUT、DELETE、PATCH 方法
- 支持 Query、Path、Body 参数输入
- JSON Body 编辑器
- 响应结果语法高亮
- 复制响应内容
- 搜索过滤接口

## 运行方式

### 前提条件
确保 XivMind 主应用正在运行（默认端口 8000）

### 启动测试系统

```bash
cd api-tester
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

然后访问 http://localhost:8001

## 项目结构

```
api-tester/
├── app/
│   ├── main.py              # 主入口
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── proxy.py        # 代理原项目接口
│   │   └── schema.py       # 加载原项目 OpenAPI schema
│   └── templates/
│       └── index.html      # 测试界面
├── requirements.txt
├── pyproject.toml
└── README.md
```
