import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("="*50)
print("AI 模块测试")
print("="*50)
print("\n1. 测试导入...")
try:
    from app.ai.processor import DocumentProcessor; print("   ✅ processor")
    from app.ai.embedding import EmbeddingClient; print("   ✅ embedding")
    from app.ai.vector_store import FAISSVectorStore; print("   ✅ vector_store")
    from app.services.rag_service import RAGService; print("   ✅ rag_service")
    print("   ✅ 所有模块导入成功")
except Exception as e:
    print(f"   ❌ {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print("\n2. 测试 Processor 切分...")
try:
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
    chunks = processor.split_text("河海大学位于南京。这是一所水利特色高校。", doc_id=1)
    print(f"   ✅ 切分成功，生成 {len(chunks)} 个块")
except Exception as e:
    print(f"   ❌ {e}")
    sys.exit(1)
print("\n3. 测试 Vector Store...")
try:
    import tempfile, numpy as np, faiss
    with tempfile.TemporaryDirectory() as tmpdir:
        store = FAISSVectorStore(index_dir=tmpdir, index_name="test")
        dim = 128
        vectors = np.random.randn(3, dim).astype(np.float32)
        faiss.normalize_L2(vectors)
        metadatas = [{"content": f"内容{i}", "doc_id": 1, "chunk_idx": i} for i in range(3)]
        store.add_vectors(vectors, metadatas)
        print(f"   ✅ 添加成功，共 {store.total_count} 个向量")
        results = store.search(vectors[0], top_k=2)
        print(f"   ✅ 检索成功，返回 {len(results)} 条结果")
except Exception as e:
    print(f"   ❌ {e}")
    sys.exit(1)
print("\n" + "="*50)
print("🎉 所有测试通过！")
print("="*50)