# AI 技术栈与依赖清单

## 项目信息
- **项目名称**：校园问答助手
- **文档作者**：陈梦（AI工程师）
- **日期**：2026年7月15日

---

## 一、AI 相关 Python 依赖包

| 包名 | 版本 | 用途说明 |
|------|------|----------|
| `dashscope` | >=1.14.0 | 阿里云百炼官方 SDK，调用 Embedding 和 Qwen LLM API |
| `faiss-cpu` | >=1.7.0 | Facebook 向量检索库，用于相似度搜索（CPU 版本） |
| `llama-index` | >=0.10.0 | RAG 框架核心，管理文档索引、检索和查询 |
| `llama-index-embeddings-dashscope` | 对应版本 | LlamaIndex 的 DashScope Embedding 适配器 |
| `llama-index-llms-dashscope` | 对应版本 | LlamaIndex 的 DashScope LLM 适配器 |
| `pypdf` | >=3.0.0 | PDF 文档解析 |
| `python-docx` | >=0.8.0 | Word 文档解析 |
| `uvicorn` | >=0.30.0 | ASGI 服务器，用于启动 FastAPI 应用 |
| `fastapi` | >=0.115.0 | 后端 Web 框架 |
| `pydantic` | >=2.0.0 | 数据验证和配置管理 |
| `python-multipart` | >=0.0.0 | 文件上传支持 |

---

## 二、AI 相关环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | DashScope API 密钥（必填） | `sk-xxxxxxxxxxxxxxxx` |
| `DASHSCOPE_EMBEDDING_MODEL` | Embedding 模型名称 | `text-embedding-v2` |
| `DASHSCOPE_LLM_MODEL` | LLM 模型名称 | `qwen-plus` |

---

## 三、向量库存储说明

| 目录 | 说明 |
|------|------|
| `backend/data/llama_index_storage/` | 向量索引主存储目录 |
| `backend/data/campus_qa.db` | SQLite 数据库（含用户、文档、会话记录） |

---

## 四、AI 环境验证命令

```bash
# 验证 Python 和 uv
python3.12 --version
uv --version

# 验证 DashScope 依赖
uv run python -c "import dashscope; print('dashscope ok')"

# 验证 FAISS
uv run python -c "import faiss; print('faiss ok')"

# 验证 LlamaIndex
uv run python -c "import llama_index; print('llama_index ok')"

