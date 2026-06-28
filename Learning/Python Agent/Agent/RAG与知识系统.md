# RAG 与知识系统

这篇文档解决一个问题：**如何构建一个真正可用的 RAG 系统**——不是跑通 demo，而是生产质量：ingestion pipeline 可靠、检索准确、回答有据可查、质量可评测。

---

## 1. RAG 解决什么问题

```
普通 LLM：用户问题 → LLM（凭训练记忆回答）→ 容易幻觉、知识过时、无私有数据

RAG：用户问题 → 检索相关文档 → 把文档片段放进 context → LLM 基于文档回答
```

**RAG 适合的场景**：私有知识库问答、需要引用来源的场景、知识频繁更新、超过 context window 的文档。

**RAG 不适合的场景**：需要复杂推理/计算的任务（用工具）；问题答案在训练数据里（LLM 自己就能答）；实时数据（直连数据库更合适）。

---

## 2. 完整 Ingestion Pipeline

RAG 的质量 80% 决定于 ingestion 阶段，不是检索阶段。

```
原始文档
  ↓ Parsing（文档解析）
  ↓ Cleaning（清洗去噪）
  ↓ Chunking（切块）
  ↓ Metadata Extraction（元数据提取）
  ↓ Embedding（向量化）
  ↓ Indexing（建索引）
知识库（向量存储 + 元数据存储）
```

### Parsing

| 文档类型 | 推荐工具 | 注意点 |
|---------|---------|--------|
| PDF | `pymupdf`, `pdfplumber`, `marker` | 扫描件需要 OCR；表格难处理 |
| Word | `python-docx` | 注意表格和图片 |
| Markdown | 直接解析 | 相对干净 |
| HTML/网页 | `trafilatura`, `BeautifulSoup` | 要去掉导航栏/广告 |
| 代码 | 按语法结构切割 | 保持函数完整性 |

```python
import fitz  # pymupdf

def parse_pdf(file_path: str) -> list[dict]:
    doc = fitz.open(file_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():  # 跳过空白页
            pages.append({
                "content": text,
                "page_num": i + 1,
                "source": file_path,
            })
    return pages
```

### Cleaning

```python
import re

def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)   # 多余空行
    text = re.sub(r' {2,}', ' ', text)         # 多余空格
    return text.strip()

def is_garbage(text: str, min_length: int = 50) -> bool:
    if len(text) < min_length:
        return True
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    return alpha_ratio < 0.3  # 字母/汉字占比太低
```

### Chunking

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 固定长度 | 按 N 个 token 切 | 简单 | 可能切断句子 |
| 按段落/标题 | 按文档结构 | 语义边界清晰 | 段落大小差异大 |
| 递归切割（推荐） | 先按大分隔符，再细分 | 平衡结构和大小 | 实现稍复杂 |
| 语义切割 | 相似度变化处切割 | 语义最完整 | 慢，成本高 |

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,           # 每块最大字符数
    chunk_overlap=100,        # 块间重叠
    separators=["\n\n", "\n", "。", ".", " ", ""],
)

chunks = splitter.split_text(cleaned_text)
```

**经验参数**：chunk_size 300-800 token；overlap 约 10-20% 的 chunk_size；代码文件按函数/类边界切，不按字符数。

### Embedding

```python
from openai import OpenAI

def embed_chunks(chunks: list[str], batch_size: int = 100) -> list[list[float]]:
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings
```

**模型选择**：`text-embedding-3-small` 适合大多数场景；本地模型（`bge-m3`）适合私有部署。

---

## 3. 向量存储与检索

### 主流向量数据库对比

| 数据库 | 部署 | 规模 | 适合 |
|--------|------|------|------|
| Chroma | 本地/embedded | 小到中 | 开发、原型 |
| Qdrant | 自托管/云 | 中到大 | 生产，功能丰富 |
| pgvector | PostgreSQL 扩展 | 中 | 已有 PostgreSQL 的场景 |
| Pinecone | 云服务 | 大 | 不想管运维 |

### 基础向量检索

```python
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct

qclient = qdrant_client.QdrantClient(":memory:")

qclient.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

def upsert_chunks(chunks: list[dict]):
    points = [
        PointStruct(
            id=chunk["id"],
            vector=chunk["embedding"],
            payload=chunk["metadata"],
        )
        for chunk in chunks
    ]
    qclient.upsert(collection_name="docs", points=points)

def search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    results = qclient.search(
        collection_name="docs",
        query_vector=query_embedding,
        limit=top_k,
    )
    return [
        {"id": str(r.id), "content": r.payload["content"], "source": r.payload["source"], "score": r.score}
        for r in results
    ]
```

---

## 4. 检索增强策略

### 混合检索（Hybrid Search）

纯向量检索对精确词汇匹配（人名、产品名、代码符号）效果差，用混合检索：

```
Hybrid Search = 向量检索（语义）+ BM25（关键词）→ RRF 融合排序
```

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    def __init__(self, vector_store, documents: list[dict]):
        # documents: [{"id": str, "content": str, ...}]
        # 与向量库使用同一套 id，BM25 通过索引位置映射回 id
        self.vector_store = vector_store
        self.doc_ids = [d["id"] for d in documents]
        self.doc_map = {d["id"]: d for d in documents}
        self.bm25 = BM25Okapi([d["content"].split() for d in documents])
    
    def retrieve(self, query: str, top_k: int = 10, alpha: float = 0.7) -> list[dict]:
        # 向量检索（召回 2× 候选，再 RRF 融合）
        query_emb = embed(query)
        vector_results = self.vector_store.search(query_emb, top_k * 2)
        # search() 返回带 "id" 字段的 dict 列表
        vector_id_map = {r["id"]: r for r in vector_results}
        
        # BM25 关键词检索
        bm25_scores = self.bm25.get_scores(query.split())
        bm25_top = sorted(
            enumerate(bm25_scores), key=lambda x: x[1], reverse=True
        )[:top_k * 2]
        
        # RRF 融合（Reciprocal Rank Fusion）
        rrf_scores: dict[str, float] = {}
        for rank, (doc_idx, _) in enumerate(bm25_top):
            doc_id = self.doc_ids[doc_idx]   # 索引位置 → 文档 id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 - alpha) / (60 + rank)
        for rank, result in enumerate(vector_results):
            doc_id = result["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + alpha / (60 + rank)
        
        top_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
        # 优先用向量检索的完整结果（含 score），回退到 doc_map
        return [
            vector_id_map.get(doc_id) or self.doc_map[doc_id]
            for doc_id in top_ids
            if doc_id in self.doc_map
        ]
```

### Query Rewriting

```python
async def rewrite_query(original_query: str) -> list[str]:
    response = await llm_call([
        {
            "role": "system",
            "content": "你是搜索 query 优化专家。给定用户问题，生成 3 个角度不同的搜索 query，用于检索相关文档。",
        },
        {
            "role": "user",
            "content": f"用户问题：{original_query}\n\n以 JSON 格式返回：{{\"queries\": [...]}}",
        },
    ])
    data = json.loads(response)
    return [original_query] + data["queries"]
```

### Reranking

向量检索的 top-k 不代表最相关，Reranker 做精排：

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    pairs = [(query, c["content"]) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), reverse=True)
    return [item for _, item in ranked[:top_k]]
```

### 最小可运行混合检索示例

下面是一个**可直接运行**的完整例子，用 Qdrant in-memory + BM25 + RRF，不依赖外部服务：

```python
# pip install qdrant-client rank-bm25 openai
import asyncio
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct
from rank_bm25 import BM25Okapi
from openai import AsyncOpenAI

oai = AsyncOpenAI()

DOCS = [
    {"id": "1", "content": "RAG 通过检索相关文档来增强 LLM 的回答质量。"},
    {"id": "2", "content": "BM25 是基于词频统计的关键词检索算法，对精确匹配效果好。"},
    {"id": "3", "content": "向量检索通过语义相似度找到相关文档，对语义理解效果好。"},
    {"id": "4", "content": "混合检索结合了 BM25 关键词和向量语义两种方式，用 RRF 融合排序。"},
    {"id": "5", "content": "Qdrant 是一个开源高性能向量数据库，支持过滤和混合检索。"},
]

async def embed(texts: list[str]) -> list[list[float]]:
    resp = await oai.embeddings.create(model="text-embedding-3-small", input=texts)
    return [item.embedding for item in resp.data]

async def build_index(docs: list[dict]):
    qc = qdrant_client.QdrantClient(":memory:")
    qc.create_collection("docs", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
    
    embeddings = await embed([d["content"] for d in docs])
    qc.upsert("docs", points=[
        PointStruct(id=int(d["id"]), vector=emb, payload={"id": d["id"], "content": d["content"]})
        for d, emb in zip(docs, embeddings)
    ])
    
    bm25 = BM25Okapi([d["content"].split() for d in docs])
    doc_ids = [d["id"] for d in docs]
    doc_map = {d["id"]: d for d in docs}
    return qc, bm25, doc_ids, doc_map

async def hybrid_search(query: str, qc, bm25, doc_ids, doc_map, top_k=3, alpha=0.7):
    [query_emb] = await embed([query])
    
    # 向量检索
    vector_hits = qc.search("docs", query_vector=query_emb, limit=top_k * 2)
    vector_results = [{"id": str(h.id), "content": h.payload["content"], "score": h.score}
                      for h in vector_hits]
    vector_id_map = {r["id"]: r for r in vector_results}
    
    # BM25 检索
    bm25_scores = bm25.get_scores(query.split())
    bm25_top = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)[:top_k * 2]
    
    # RRF 融合
    rrf: dict[str, float] = {}
    for rank, (idx, _) in enumerate(bm25_top):
        rrf[doc_ids[idx]] = rrf.get(doc_ids[idx], 0) + (1 - alpha) / (60 + rank)
    for rank, r in enumerate(vector_results):
        rrf[r["id"]] = rrf.get(r["id"], 0) + alpha / (60 + rank)
    
    top_ids = sorted(rrf, key=rrf.get, reverse=True)[:top_k]
    return [vector_id_map.get(i) or doc_map[i] for i in top_ids]

async def main():
    qc, bm25, doc_ids, doc_map = await build_index(DOCS)
    query = "向量和关键词混合检索如何实现"
    results = await hybrid_search(query, qc, bm25, doc_ids, doc_map)
    for r in results:
        print(f"[{r['id']}] {r['content']}")

asyncio.run(main())
```

**关键点**：`doc_ids` 数组保持 BM25 的枚举索引和实际文档 id 之间的映射，是两套检索系统能统一做 RRF 的关键。

---

## 5. Generation 与 Grounding

```python
def generate_with_context(query: str, docs: list[dict]) -> str:
    context = "\n\n".join([
        f"[来源: {d['source']}]\n{d['content']}"
        for d in docs
    ])
    
    messages = [
        {
            "role": "system",
            "content": (
                "请基于提供的参考资料回答问题。\n"
                "要求：只使用参考资料中的信息；如果资料不足，明确说明；"
                "回答末尾标注来源；不要捏造资料中没有的内容。"
            ),
        },
        {
            "role": "user",
            "content": f"参考资料：\n{context}\n\n问题：{query}",
        },
    ]
    
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content
```

---

## 6. RAG 评估

### 三层评估

| 层次 | 指标 | 含义 | 工具 |
|------|------|------|------|
| Retrieval | Recall@k, Precision@k | 检索召回率和精确率 | 手工标注 |
| Generation | Faithfulness | 回答是否完全基于文档 | RAGAS |
| Generation | Answer Relevance | 回答是否回应了问题 | RAGAS |
| End-to-end | Task Success | 最终回答是否正确 | 人工评估 |

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

results = evaluate(
    dataset=eval_dataset,  # 含 question, contexts, answer, ground_truth
    metrics=[faithfulness, answer_relevancy, context_recall],
)
print(results)
```

**Faithfulness 最重要**：它衡量回答是否完全基于检索到的文档，没有幻觉。

---

## 7. 知识库治理

| 问题 | 表现 | 解决方案 |
|------|------|---------|
| 知识过期 | 回答旧政策 | 设 TTL，定期重新 ingestion |
| 重复内容 | 同一段话检索出多次 | ingestion 时去重 |
| 低质量文档 | 检索出垃圾内容 | 数据质量评分 + 过滤 |
| 敏感信息 | 检索出不该给用户看的内容 | 文档级权限控制 |

---

## 8. 面试高频

**Q：RAG 和 Fine-tuning 怎么选？**

> RAG 和 Fine-tuning 解决不同问题。RAG 解决"模型没有某个知识"——在推理时把知识注入 context。Fine-tuning 解决"模型的行为/风格/输出格式不对"——改变模型本身。如果问题是"模型不知道公司内部产品信息"，用 RAG。如果问题是"模型回答格式总是不符合要求"，用 Fine-tuning。如果两个问题都有，先 RAG + prompt 解决知识问题，再考虑 Fine-tuning 解决格式问题。

**Q：RAG 里 chunk size 多大合适？**

> 没有绝对答案，取决于文档类型和任务。经验原则：太小（<200 token）上下文不足；太大（>1500 token）检索精度下降。常用范围 400-800 token，加 10-15% 的 overlap。代码文件按函数/类边界切，不要按字符数切。建议用不同 chunk size 做 retrieval 评估，看哪个召回率最高。

**Q：为什么 RAG 系统的检索准确率上不去，该从哪里排查？**

> 按优先级：一是数据质量（parsing 出来的内容是否干净，有没有乱码）；二是 chunking 策略（chunk 是否在语义边界切割）；三是 embedding 模型（通用模型对专业术语可能表现差）；四是 query rewriting（用户原始 query 不是最优检索 query）；五是检索策略（纯向量检索对关键词匹配差，试试混合检索 + reranking）。大多数时候，数据质量是最根本的问题。
