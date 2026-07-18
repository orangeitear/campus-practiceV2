
---

## 文档二：JWT认证技术说明.md

```markdown
# JWT 认证技术说明

**文档版本**：v1.0  
**日期**：2026-07-16  
**作者**：陈梦  


## 一、Token 机制

采用 PyJWT 生成和解析 Token，流程如下：

**Token 结构**：
- Header：加密算法（HS256）
- Payload：用户 ID、用户名、角色、过期时间
- Signature：使用 Secret Key 签名


## 二、FastAPI Depends 依赖注入校验流程

**核心依赖函数**：`get_current_user`

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 1. 解析 Token
    # 2. 校验过期时间
    # 3. 查询用户信息
    # 4. 返回用户对象或抛出异常