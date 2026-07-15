**校园问答助手开发项目**

Git 分支协作操作指南

仓库分支已配置：main（稳定分支）+ dev（开发分支），每位成员按以下流程从 dev 拉取自己的 feature 分支工作

**一、通用操作流程（所有人必看）**

**1.1 第一次：克隆仓库**

每个人第一次需要把仓库克隆到本地，终端里执行：

git clone https://github.com/your-team/campus-qa.git
cd campus-qa

把上面的仓库地址换成你们组实际的 GitHub 仓库地址。

**1.2 每次工作前：同步 dev 最新代码**

每天开始工作前，先确保本地 dev 是最新的：

git checkout dev
git pull origin dev

**1.3 创建自己的 feature 分支**

从 dev 分支创建自己的功能分支，分支名按 "feature/功能名" 格式：

git checkout -b feature/你的功能名

分支名要用英文小写，单词之间用连字符 - 连接，不要用中文。

**1.4 开发过程中提交代码**

开发过程中，建议完成一个小功能就提交一次：

git status                    # 查看修改了哪些文件
git add .                     # 添加所有修改到暂存区
git commit -m "type(scope): 描述"  # 按规范写提交信息
git push origin feature/你的功能名

提交信息格式参考：

feat(chat): 实现聊天消息气泡组件

fix(api): 修复登录接口参数校验错误

docs: 更新接口说明文档

chore: 配置 .gitignore

**1.5 开发完成后：发起 Pull Request（PR）**

功能开发完成后，不要直接推送到 main 或 dev，要在 GitHub 上发起 Pull Request：

**① 打开 GitHub 仓库页面**

② 点击 "Compare & pull request" 或 "Pull requests" 标签页 → "New pull request"

**③ Base 分支一定要选择 dev（不要选 main！）**

④ Compare 分支选择你的 feature/你的功能名

⑤ 填写 PR 标题和描述，点击 "Create pull request"

⑥ 等待组长或指定成员审核，通过后点击 "Merge pull request" 合并到 dev

⑦ 合并后删除该 feature 分支，本地执行：

git checkout dev
git pull origin dev
git branch -d feature/你的功能名

**1.6 几个绝对不能做的事**

❌ 不要直接 push 到 main 分支

❌ 不要直接 push 到 dev 分支（特殊情况组长除外）

❌ 不要提交 .env、密码、密钥、node_modules、target 文件夹

❌ 提交信息不要写 "111"、"aaa"、"改了东西" 这种无意义内容

✅ 只做自己的 feature 分支，完成后发 PR 合并到 dev

**二、按角色分配的具体分支任务**

**2.1 易宁星（组长 / 产品经理 / 后端开发）**

负责仓库管理、后端基础架构、统一协调。

**你的 feature 分支：**

**feature/backend-init**

**feature/project-management**

**具体操作：**

① 创建并管理 dev 分支（已配置完成）

② 审核其他成员发起的 Pull Request

③ 从 dev 创建自己的 feature/backend-init 分支：

git checkout dev
git pull origin dev
git checkout -b feature/backend-init
git push origin feature/backend-init

④ 在该分支上完成以下工作：

   - 配置后端项目基础结构（Spring Boot 项目骨架、application.yml）

   - 集成 MyBatis-Plus、MySQL、Swagger

   - 编写统一返回结果类（Result / ResponseWrapper）

   - 编写全局异常处理

⑤ 完成后发起 PR 到 dev，标题示例：

   feat(backend): 初始化 Spring Boot 后端项目结构

⑥ 定期将 dev 合并到 main（由组长操作）：

git checkout main
git pull origin main
git merge dev
git push origin main

**2.2 汤俊贤（前端开发）**

负责前端项目初始化、页面开发。

**你的 feature 分支：**

**feature/frontend-init**

**feature/login-page**

**feature/chat-page**

**具体操作：**

① 从 dev 创建自己的 feature/frontend-init 分支：

git checkout dev
git pull origin dev
git checkout -b feature/frontend-init
git push origin feature/frontend-init

② 在该分支上完成以下工作：

   - 用 Vite 初始化 React + TypeScript 项目

   - 安装依赖：Ant Design、Tailwind CSS、Axios、React Router

   - 配置 Vite 代理（/api -> http://localhost:8080）

   - 配置前端目录结构（pages / components / services / utils）

③ 完成后发起 PR 到 dev，标题示例：

   feat(frontend): 初始化 Vite + React 前端项目

④ 后续页面开发每个功能单独建分支：

git checkout dev
git pull origin dev
git checkout -b feature/login-page
# 开发登录页...
git push origin feature/login-page

⑤ 在 GitHub 发起 PR，合并到 dev

**2.3 王嘉欣（后端开发）**

负责数据库设计、后端业务接口开发。

**你的 feature 分支：**

**feature/database-schema**

**feature/user-api**

**feature/document-api**

**具体操作：**

① 从 dev 创建自己的 feature/database-schema 分支：

git checkout dev
git pull origin dev
git checkout -b feature/database-schema
git push origin feature/database-schema

② 在该分支上完成以下工作：

   - 在 sql/ 目录下编写 schema.sql

   - 创建 sys_user、kb_document、qa_record 三张表

   - 绘制 ER 图，放到 docs/database/ 目录

③ 完成后发起 PR 到 dev，标题示例：

   feat(database): 设计并创建 MySQL 数据库表结构

④ 后续接口开发：

git checkout dev
git pull origin dev
git checkout -b feature/user-api
# 开发用户相关接口...
git push origin feature/user-api

⑤ 每个功能完成后都发 PR 到 dev，不要一次性做太多功能

**2.4 陈梦（AI 工程师）**

负责 RAG 架构、向量库、AI 模型接入。

**你的 feature 分支：**

**feature/ai-config**

**feature/rag-service**

**feature/vector-store**

**具体操作：**

① 从 dev 创建自己的 feature/ai-config 分支：

git checkout dev
git pull origin dev
git checkout -b feature/ai-config
git push origin feature/ai-config

② 在该分支上完成以下工作：

   - 配置 AI 调用环境（DashScope API Key 写到本地 .env，不要提交）

   - 编写 RAG 服务类：文档切分、Embedding、FAISS 检索、Prompt 工程

   - 测试向量库加载和问答功能

③ 完成后发起 PR 到 dev，标题示例：

   feat(ai): 配置 DashScope 并接入 RAG 问答服务

④ 向量库文件较大，不要提交到 GitHub，已在 .gitignore 中排除：

vector_store/
faiss_index/
llama_index_storage/

⑤ 在 README 中补充 AI 环境配置说明，提交信息示例：

   docs(ai): 添加 DashScope API 配置说明

**三、提交信息规范速查表**

**类型**

**含义**

**示例**

**feat**

新功能

feat(chat): 实现聊天消息列表组件

**fix**

修复 Bug

fix(login): 修复登录状态未持久化

**docs**

文档变更

docs: 更新数据库设计说明

**style**

代码格式

style: 统一后端代码缩进

**refactor**

重构

refactor(service): 重构 RAG 检索逻辑

**test**

测试

test(user): 添加用户登录单元测试

**chore**

构建/工具

chore: 配置 .gitignore

**四、常见问题处理**

**4.1 拉取代码时提示冲突**

git stash                 # 先把本地修改藏起来
git pull origin dev       # 拉最新代码
git stash pop             # 恢复自己的修改
# 手动解决冲突后重新提交
git add .
git commit -m "merge: 同步 dev 分支最新代码"

**4.2 自己分支落后于 dev，想同步 dev 最新内容**

git checkout feature/你的功能名
git merge dev
# 解决冲突后
git add .
git commit -m "merge: 同步 dev 最新代码"
git push origin feature/你的功能名

**4.3 忘记新建分支，直接在 dev 上修改了**

如果还没有提交：

git stash
git checkout -b feature/新分支名
git stash pop

如果已经提交到 dev 了（且你是组长或误操作）：

git reset --soft HEAD~1   # 撤回最近一次提交（保留修改）
git stash
git checkout -b feature/新分支名
git stash pop

**4.4 误提交了 .env 或 node_modules**

git rm --cached .env      # 从 git 跟踪中移除
git rm -r --cached node_modules
git commit -m "chore: 移除误提交的环境配置文件"

然后确保 .gitignore 里已经包含这些文件。

**五、分支任务分配表**

**成员**

**角色**

**今日 feature 分支**

**主要工作内容**

易宁星

组长/PM/后端

feature/backend-init

后端项目初始化、审核 PR

汤俊贤

前端开发

feature/frontend-init

Vite + React 项目初始化

王嘉欣

后端开发

feature/database-schema

MySQL 数据库表结构设计

陈梦

AI 工程师

feature/ai-config

RAG 环境配置、AI 服务接入

组长：易宁星      日期：____________