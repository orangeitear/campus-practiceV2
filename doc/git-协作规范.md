# Git 协作规范

## 一、分支策略

| 分支 | 用途 | 来源 | 合并去向 | 谁来操作 |
|------|------|------|---------|---------|
| `main` | 生产环境，稳定可用版本 | — | — | 仅组长合并 |
| `dev` | 日常开发集成分支 | main | main | 组长合并 |
| `feature/xxx` | 功能开发分支 | dev | dev | 个人创建、PR 合并 |
| `fix/xxx` | Bug 修复分支 | dev | dev | 个人创建、PR 合并 |

### 规则

1. **永远不要直接往 main 提交代码**，main 只接受从 dev 合并
2. **所有开发在 feature 分支进行**，完成后发起 Pull Request 合并到 dev
3. **dev 分支定期合并到 main**（由组长操作，比如每个 Day 结束时）
4. **每人只在自己的分支上开发**，不要动别人的分支

---

## 二、分支命名规范

```
feature/功能描述      如：feature/user-login
fix/问题描述          如：fix/chat-crash
docs/文档描述         如：docs/api-spec
```

命名用英文小写，单词用连字符 `-` 分隔，见名知意。

---

## 三、提交信息规范（Conventional Commits）

每次 commit 必须按以下格式写信息：

```
<type>(<scope>): <description>
```

### type 类型

| type | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(chat): 实现智能问答聊天界面` |
| `fix` | 修复 Bug | `fix(login): 修复登录后跳转错误` |
| `docs` | 文档变更 | `docs: 添加数据库设计文档` |
| `style` | 代码格式 | `style: 统一缩进为 4 空格` |
| `refactor` | 重构 | `refactor(api): 重构用户接口返回格式` |
| `test` | 测试 | `test(auth): 添加登录接口单元测试` |
| `chore` | 构建/工具 | `chore: 配置 .gitignore` |

### scope 可选范围

`auth` `chat` `document` `user` `database` `frontend` `backend` `ai` 等

---

## 四、日常工作流程（每个成员都要遵守）

### 1. 每天开始工作前

```bash
# 切换到 dev 分支，拉取最新代码
git checkout dev
git pull origin dev

# 从 dev 创建自己的功能分支
git checkout -b feature/你的功能名
```

### 2. 开发过程中，分批提交

```bash
# 查看改了哪些文件
git status

# 添加修改的文件
git add .

# 提交（必须写规范的 commit 信息！）
git commit -m "feat(user): 实现用户注册接口"
```

### 3. 推送到远程仓库

```bash
git push origin feature/你的功能名
```

### 4. 在 GitHub 上发起 Pull Request

- 打开 GitHub 仓库页面
- 点击 "Compare & pull request"
- **Base 分支选 dev**（不是 main！）
- 填写 PR 标题和说明
- 点击 "Create pull request"

### 5. 审核合并

- 组长（或指定审核人）审核代码
- 审核通过后点击 "Merge pull request"
- 合并后删除 feature 分支

### 6. 合并后同步本地

```bash
git checkout dev
git pull origin dev

# 删除本地已合并的功能分支
git branch -d feature/你的功能名
```

---

## 五、常见情况处理

### 情况 1：拉取 dev 时有冲突

```bash
git checkout dev
git pull origin dev
# 如果报错有冲突，先 stash 自己的修改
git stash
git pull origin dev
git stash pop
# 手动解决冲突后重新提交
```

### 情况 2：feature 分支落后于 dev，需要同步

```bash
git checkout feature/你的功能名
git merge dev
# 解决冲突后提交
git add .
git commit -m "merge: 同步 dev 分支最新代码"
```

### 情况 3：不小心提交了不该提交的文件

```bash
# 撤销最近一次提交（保留修改）
git reset --soft HEAD~1
# 从暂存区移除不该提交的文件
git rm --cached .env  # 例如 .env 文件
git commit -m "chore: 移除误提交的 .env 文件"
```

---

## 六、Pull Request 模板

发起 PR 时，描述按以下格式写：

```
## 修改内容
简要描述本次 PR 做了什么

## 修改类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档 (docs)
- [ ] 重构 (refactor)

## 测试情况
描述如何测试的，结果如何

## 关联说明
其他需要审核人知道的注意事项
```
