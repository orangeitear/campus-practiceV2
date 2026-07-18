```markdown
# RAG 技术选型方案

**文档版本**：v1.0  
**日期**：2026-07-16  
**作者**：陈梦  


## 技术栈选型

### 一、Embedding 模型

**选型**：阿里云 DashScope `text-embedding-v2`

**选型理由**：
- 语种覆盖广，支持中、英、日、韩、德、俄等多语言，适合校园多语言资料场景
- 向量维度可选（768 / 1536），资源受限时可降维节省存储与计算成本
- 与 DashScope LLM 同生态，调用便捷，减少多平台接入复杂度

**使用方式**：
```python
import os
import dashscope

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
```


### 二、向量库

**选型**：FAISS（本地部署）

**选型理由**：
- 零外部依赖，`pip install faiss-cpu` 即可使用，部署成本低
- 索引可持久化到本地磁盘，无需购买云向量数据库
- 支持高效的 ANN 检索，适合百万级向量规模

**存储方案**：
- `faiss.index`：存储向量数据
- `metadata.json`：存储原文、来源等元数据

**分块策略**：采用固定大小切分 + 重叠（重叠避免边界信息丢失）


### 三、LLM API

**选型**：阿里云 DashScope 通义千问

**模型选择**：
- `qwen-turbo`：响应快、成本低，适合实时问答（起步推荐）
- `qwen-max`：推理能力强，适合高精度问答
- `qwen-long`：支持长文档，适合长文本理解与分析

**鉴权方式**：
```python
import os
import dashscope

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
```

⚠️ API Key 必须通过环境变量读取，严禁硬编码。

**超时与重试策略**：
- 超时时间：30 秒
- 最大重试次数：3 次
- 重试间隔：指数退避（1s → 2s → 4s）
- 降级方案：模型不可用时返回友好提示


### 四、整体架构

```
文档上传 → 文本切分 → Embedding向量化 → FAISS存储（离线索引）
                                            ↓
用户提问 → Embedding向量化 → FAISS检索TopK → 拼接上下文 → LLM生成回答（在线问答）
```


### 五、Day3 开发任务

- [ ] FAISS 向量存储与检索封装
- [ ] DashScope Embedding 调用封装
- [ ] 文档切分模块
- [ ] LLM 问答接口与超时重试机制
- [ ] RAG 问答流程串联


*本方案为 Day3 RAG 开发提供技术选型依据。*
```