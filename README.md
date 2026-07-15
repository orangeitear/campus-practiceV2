# 校园问答助手

> 基于 LLM + RAG 的校园智能问答 Web 应用系统

## 项目简介

校园问答助手是一个面向校园场景的智能问答系统，用户通过 Web 浏览器提问，系统基于知识库文档进行 RAG 检索，调用大语言模型生成精准回答。

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 前端 | React 18 + TypeScript + Vite + Ant Design + Tailwind CSS |
| 后端 | Spring Boot 3.x + MyBatis-Plus |
| 数据库 | MySQL 8.0 |
| AI 引擎 | 通义千问 / OpenAI API + FAISS 向量检索 |
| 工具 | Git + Swagger + Postman |

## 团队成员

| 姓名 | 角色 | 职责 |
|------|------|------|
| 易宁星 | 组长 / 产品经理 / 后端开发 | 项目管理、需求分析、后端开发、仓库管理 |
| 汤俊贤 | 前端开发 | 前端页面开发、UI 实现 |
| 王嘉欣 | 后端开发 | 后端接口开发、数据库设计 |
| 陈梦 | AI 工程师 | RAG 架构、AI 模型对接、向量库管理 |

> 测试由全体成员共同完成

## 项目结构

```
campus-qa/
├── frontend/          # 前端项目（React + Vite）
├── backend/           # 后端项目（Spring Boot）
├── docs/              # 项目文档
│   ├── architecture/  # 架构设计图
│   ├── database/      # 数据库设计
│   └── api/           # 接口文档
├── sql/               # SQL 建表脚本
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- JDK 17+
- Node.js 20+
- MySQL 8.0+
- Git

### 后端启动

```bash
cd backend
# 配置数据库连接（修改 application.yml）
mvn spring-boot:run
# 访问 http://localhost:8080
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## 分支策略

- `main`：生产分支，只接受来自 dev 的合并，保持稳定可用
- `dev`：开发分支，日常开发的集成分支
- `feature/xxx`：功能分支，从 dev 拉出，完成后合并回 dev
- `fix/xxx`：修复分支，从 dev 拉出，修复后合并回 dev

详见 [Git 协作规范](./docs/git-协作规范.md)

## 提交规范

遵循 Conventional Commits：

```
<type>(<scope>): <description>

type 可选值：
  feat     新功能
  fix      修复 Bug
  docs     文档变更
  style    代码格式（不影响功能）
  refactor 重构
  test     测试相关
  chore    构建/工具变更
```

示例：`feat(auth): 实现用户登录接口`
