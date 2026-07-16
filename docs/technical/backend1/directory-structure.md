\# 后端目录结构说明



> 项目后端基于 \*\*FastAPI\*\* 框架，使用 \*\*uv\*\* 作为包管理器。以下为当前目录结构及核心文件说明。

backend/

├── app/ # 应用主代码目录

│ ├── main.py # FastAPI 应用入口，注册路由和中间件

│ ├── routers/ # API 路由模块（按功能拆分）

│ │ ├── documents.py # 知识库文档相关接口（上传、列表、删除）

│ │ ├── chat.py # 问答聊天接口（发送问题、历史记录）

│ │ └── health.py # 系统健康检查接口

│ ├── models/ # 数据模型（Pydantic + SQLAlchemy）

│ │ ├── schemas.py # Pydantic 请求/响应模型

│ │ └── database.py # SQLAlchemy ORM 模型定义

│ ├── services/ # 业务逻辑层（核心功能）

│ │ ├── rag\_engine.py # RAG 检索与生成引擎（核心）

│ │ ├── document\_processor.py # 文档上传、解析与预处理

│ │ └── llm\_client.py # DashScope LLM 调用封装

│ ├── core/ # 核心配置与工具

│ │ ├── config.py # 应用配置（读取 .env 环境变量）

│ │ ├── logger.py # 日志配置

│ │ └── exceptions.py # 自定义异常处理

│ └── utils/ # 工具函数

│ ├── file\_utils.py # 文件读写与路径处理

│ └── text\_utils.py # 文本切分、清洗等预处理

├── data/ # 数据存储目录

│ └── llama\_index\_storage/ # FAISS 向量索引文件（预构建，由 download-demo-index.py 下载）

├── tests/ # 单元测试与集成测试

├── .env # 环境变量配置（API Key 等，已加入 .gitignore，不提交）

├── .env.example # 环境变量模板文件（提交到仓库）

├── pyproject.toml # 项目依赖与 uv 配置

├── uv.lock # 锁定依赖版本（确保一致性）

└── README.md # 项目说明文档



\## 核心文件说明



\### `app/main.py`

\- \*\*作用\*\*：应用入口文件。负责初始化 FastAPI 应用、注册路由、加载向量库、初始化 RAG 引擎。

\- \*\*关键日志\*\*：启动时输出 `✔ LlamaIndex 索引已加载: 13 个节点` 表示向量库加载成功。



\### `app/services/rag\_engine.py`

\- \*\*作用\*\*：RAG 核心逻辑。包含文档向量化、FAISS 检索、Prompt 构建和 LLM 调用。

\- \*\*依赖\*\*：`dashscope`、`llama-index`、`faiss-cpu`。



\### `app/models/database.py`

\- \*\*作用\*\*：定义数据库表结构（SQLAlchemy ORM 模型），与 `docs/database/schema.sql` 对应。

\- \*\*核心表\*\*：`sys\_user`、`kb\_document`、`qa\_record`。



\### `data/llama\_index\_storage/`

\- \*\*作用\*\*：存放预构建的 FAISS 向量索引文件，由 `download-demo-index.py` 下载。后端启动时自动加载。

\- \*\*注意\*\*：该目录由脚本生成，不需要手动创建。



\### `.env` 与 `.env.example`

\- `.env`：存放敏感信息（如 `DASHSCOPE\_API\_KEY`），已加入 `.gitignore`，\*\*绝不提交\*\*。

\- `.env.example`：模板文件，提交到仓库，供团队成员参考配置。



\## 环境与依赖管理



\- \*\*Python 版本\*\*：3.12+

\- \*\*包管理器\*\*：uv

\- \*\*安装依赖\*\*：`uv sync --extra dev`（自动创建虚拟环境 `.venv`）

\- \*\*启动服务\*\*：`uv run uvicorn app.main:app --reload`



\## 设计思路



\- \*\*分层设计\*\*：路由层（`routers/`） → 业务逻辑层（`services/`） → 数据模型层（`models/`），职责清晰。

\- \*\*配置分离\*\*：敏感配置通过 `.env` 管理，避免硬编码。

\- \*\*RAG 流程\*\*：文档 → 切分 → Embedding → FAISS 检索 → LLM 生成 → 返回答案，各环节解耦。



