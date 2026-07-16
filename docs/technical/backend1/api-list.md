\# 后端 API 接口清单



> 本清单基于项目 Swagger 文档（`/docs`）整理，按模块分类。



\## 基础信息

\- 根路径：`/api/v1`（如适用）

\- 认证方式：待定（可能使用 API Key 或 JWT）



\---



\## 1. 健康检查与系统状态

| 方法 | URL | 功能 | 请求参数 | 返回值 |

|------|-----|------|----------|--------|

| GET | `/health` 或 `/` | 服务健康检查 | 无 | `{"status": "ok"}` |



\---



\## 2. 知识库文档管理

| 方法 | URL | 功能 | 请求参数 | 返回值 |

|------|-----|------|----------|--------|

| POST | `/documents/upload` | 上传文档文件 | `file` (multipart/form-data) | `{"document\_id": "xxx", "status": "processing"}` |

| GET | `/documents` | 获取文档列表 | `page`, `size` (可选) | 文档列表（含分页信息） |

| GET | `/documents/{document\_id}` | 获取文档详情 | `document\_id` (路径参数) | 文档详细信息 |

| DELETE | `/documents/{document\_id}` | 删除文档 | `document\_id` (路径参数) | `{"message": "deleted"}` |

| GET | `/documents/{document\_id}/status` | 获取文档处理状态 | `document\_id` | `{"status": "completed/processing/failed"}` |



\---



\## 3. 问答（Chat）接口

| 方法 | URL | 功能 | 请求参数 | 返回值 |

|------|-----|------|----------|--------|

| POST | `/chat` | 发送问题并获取 AI 回答 | `{"question": "xxx", "session\_id": "xxx"}` | `{"answer": "xxx", "sources": \[...]}` |

| GET | `/chat/history` | 获取历史对话记录 | `session\_id` (查询参数) | 对话记录列表 |



\---



\## 4. 其他可能接口（根据 Swagger 补充）

| 方法 | URL | 功能 | 请求参数 | 返回值 |

|------|-----|------|----------|--------|

| GET | `/docs` | Swagger 交互式文档（自动生成） | 无 | HTML 页面 |



\---



\## 状态码说明

\- `200 OK`：请求成功

\- `400 Bad Request`：请求参数错误

\- `404 Not Found`：资源不存在

\- `500 Internal Server Error`：服务器内部错误



> \*\*注意\*\*：本清单基于当前代码版本整理。如启动后端服务后 Swagger 文档有新增或修改接口，请以实际 `/docs` 页面为准，并更新本清单。

