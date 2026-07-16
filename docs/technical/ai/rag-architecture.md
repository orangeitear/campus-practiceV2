# RAG 架构与工作流程说明

## 项目信息
- **项目名称**：校园问答助手
- **文档作者**：陈梦（AI工程师）
- **日期**：2026年7月15日

---

## 一、什么是 RAG？

RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合**信息检索**和**大语言模型生成**的技术方案。它先根据用户问题从知识库中检索相关文档片段，再将这些片段作为上下文输入给 LLM 生成答案，从而提升回答的准确性和时效性。

---

## 二、系统 RAG 完整工作流程

本项目的 RAG 流程共分为 **6 个核心环节**：

| 阶段 | 环节 | 技术实现 | 说明 |
|------|------|----------|------|
| 1 | 文档切分（Chunking） | LlamaIndex + 固定长度切分 | 将上传的 PDF / Word / TXT 切分为语义完整的文本块（chunk） |
| 2 | 向量化（Embedding） | DashScope `text-embedding-v2` | 将每个 chunk 转为 1536 维浮点向量 |
| 3 | 向量存储与索引 | FAISS (CPU 版本) | 构建向量索引，存储于 `backend/data/` 目录 |
| 4 | 向量检索（Retrieval） | FAISS 余弦相似度检索 | 用户提问后，检索 Top-K 个最相关的 chunk |
| 5 | Prompt 拼接 | 自定义 Prompt 模板 | 将检索结果 + 用户问题拼接为 LLM 输入 |
| 6 | LLM 生成 | DashScope Qwen 系列模型 | 流式生成答案，逐字返回给前端 |

---

## 三、数据流转说明

用户通过前端页面输入问题，请求发送到后端 `/api/chat/stream` 接口。

后端收到问题后，执行以下流程：

**第一步**：将用户问题转换为向量（调用 DashScope Embedding 模型），用这个向量去 FAISS 向量库中检索，找出语义最相似的 Top-K 个文档片段。

**第二步**：将检索到的文档片段和用户原始问题拼接成一个完整的 Prompt（包含角色设定、上下文文档、用户问题三部分）。

**第三步**：将 Prompt 发送给 DashScope 的 Qwen 大语言模型，开启流式生成模式。

**第四步**：模型生成的答案通过 SSE（Server-Sent Events）协议逐字流式返回给前端，用户看到的是打字机效果（逐字出现）。

**第五步**：流式传输结束后，后端将本次问答记录（用户问题 + AI 答案 + 会话 ID）写入 SQLite 数据库，完成持久化存储。

---

## 四、技术选型说明

| 组件 | 技术选型 | 选型理由 |
|------|----------|----------|
| Embedding 模型 | DashScope `text-embedding-v2` | 阿里云百炼提供，中文效果好，有免费额度 |
| 向量库 | FAISS (CPU) | 轻量级，无需 GPU，适合本地开发 |
| RAG 框架 | LlamaIndex | 生态完整，支持多种文档格式解析 |
| LLM | DashScope Qwen | 国内模型，中文能力强，API 稳定 |
| 后端框架 | FastAPI | 异步支持好，天然适配 SSE 流式响应 |
| 通信协议 | Server-Sent Events (SSE) | 支持流式逐字输出，用户体验好 |

---

## 五、关键代码文件说明

| 文件路径 | 功能说明 |
|----------|----------|
| `app/rag_engine_v2.py` | RAG 引擎核心类 `HHURAGEngine`，封装了加载索引、检索、生成全流程 |
| `app/rag.py` | 文档文本提取工具（PDF / DOCX / TXT 解析） |
| `app/main.py` | FastAPI 主入口，包含 `/api/chat/stream` 流式问答接口 |
| `scripts/download-demo-index.py` | 预构建向量库下载脚本 |
| `data/llama_index_storage/` | 向量索引存储目录 |

---

## 六、遇到的问题与解决方案

| 问题 | 解决方案 |
|------|----------|
| 向量库下载失败 | 使用脚本自动下载，或手动从 GitHub Release 获取 |
| API Key 未配置 | 在 `.env` 中设置 `DASHSCOPE_API_KEY` |
| 数据库种子数据冲突 | 删除 `data/campus_qa.db` 重新初始化 |
| 问答接口路径不明确 | 实际路径为 `POST /api/chat/stream`，非 `/api/qa/ask` |

---

## 七、参考资料

- [DashScope 官方文档](https://dashscope.aliyun.com/)
- [LlamaIndex 官方文档](https://docs.llamaindex.ai/)
- [FAISS 官方文档](https://faiss.ai/)
