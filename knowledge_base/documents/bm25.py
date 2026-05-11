from django.contrib.postgres.search import SearchQuery, SearchRank
from .models import Document
from .models import DocumentChunk
from .embedding import get_embedding, cosine_similarity
from api.models import AIConfig
import json


def search_fulltext(query: str, knowledge_base_id: int = None, top_k: int = 5):
    """
    使用 PostgreSQL 全文索引搜索文档
    query: 查询字符串
    knowledge_base_id: 知识库ID（可选）
    top_k: 返回前k个结果
    returns: [(doc_id, score, title, content), ...]
    """
    if not query.strip():
        return []

    # 构建搜索查询
    search_query = SearchQuery(query, config='chinese')
    
    # 过滤已发布的文档
    documents = Document.objects.filter(publish_status='published')
    
    # 如果指定了知识库，添加过滤条件
    if knowledge_base_id:
        documents = documents.filter(directory__knowledge_base_id=knowledge_base_id)
    
    # 计算相关性排名并过滤匹配的文档
    documents = documents.annotate(
        rank=SearchRank('search_vector', search_query)
    ).filter(
        search_vector=search_query
    ).order_by('-rank', '-updated_at')[:top_k]
    
    # 转换结果格式
    results = []
    max_rank = 0.0
    temp_results = []
    for doc in documents:
        rank = float(doc.rank) if doc.rank else 0.0
        max_rank = max(max_rank, rank)
        temp_results.append((doc.id, rank, doc.title, doc.content or ''))
    
    # 归一化到 0-1 范围（如果有结果）
    if max_rank > 0:
        for doc_id, rank, title, content in temp_results:
            normalized_score = rank / max_rank
            results.append((doc_id, normalized_score, title, content))
    else:
        results = temp_results
    
    return results


def search_vector(query: str, knowledge_base_id: int = None, top_k: int = 5):
    """
    使用向量相似度搜索文档chunk
    query: 查询字符串
    knowledge_base_id: 知识库ID（可选）
    top_k: 返回前k个结果
    returns: [(doc_id, score, title, chunk_content), ...]
    """
    if not query.strip():
        return []
    
    # 获取AI配置
    ai_config = AIConfig.objects.first()
    if not ai_config or not ai_config.embedding_api_key:
        return []
    
    # 生成查询向量
    query_embedding = get_embedding(
        query,
        ai_config.embedding_api_key,
        ai_config.embedding_base_url,
        ai_config.embedding_model_name
    )
    
    if query_embedding is None:
        return []
    
    # 过滤chunk
    chunks = DocumentChunk.objects.filter(
        document__publish_status='published',
        embedding__isnull=False
    ).select_related('document')
    
    # 如果指定了知识库，添加过滤条件
    if knowledge_base_id:
        chunks = chunks.filter(document__directory__knowledge_base_id=knowledge_base_id)
    
    # 计算相似度
    results = []
    for chunk in chunks:
        try:
            chunk_embedding = json.loads(chunk.embedding)
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            results.append({
                'document_id': chunk.document.id,
                'title': chunk.document.title,
                'content': chunk.content,
                'similarity': similarity
            })
        except (json.JSONDecodeError, TypeError):
            continue
    
    # 排序并去重（按文档合并）
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # 去重，每个文档只保留最相关的chunk
    seen_docs = set()
    unique_results = []
    for result in results:
        if result['document_id'] not in seen_docs:
            seen_docs.add(result['document_id'])
            unique_results.append((
                result['document_id'],
                result['similarity'],
                result['title'],
                result['content']
            ))
            if len(unique_results) >= top_k:
                break
    
    return unique_results


def search_hybrid(query: str, knowledge_base_id: int = None, top_k: int = 5, 
                  fulltext_weight: float = 0.4, vector_weight: float = 0.6):
    """
    混合检索：结合全文检索和向量检索
    query: 查询字符串
    knowledge_base_id: 知识库ID（可选）
    top_k: 返回前k个结果
    fulltext_weight: 全文检索权重
    vector_weight: 向量检索权重
    returns: [(doc_id, score, title, content), ...]
    """
    # 获取两种检索结果
    fulltext_results = search_fulltext(query, knowledge_base_id, top_k * 2)
    vector_results = search_vector(query, knowledge_base_id, top_k * 2)
    
    # 合并结果
    doc_scores = {}
    
    # 处理全文检索结果
    for doc_id, score, title, content in fulltext_results:
        if doc_id not in doc_scores:
            doc_scores[doc_id] = {
                'score': 0,
                'title': title,
                'content': content
            }
        doc_scores[doc_id]['score'] += score * fulltext_weight
    
    # 处理向量检索结果
    for doc_id, score, title, content in vector_results:
        if doc_id not in doc_scores:
            doc_scores[doc_id] = {
                'score': 0,
                'title': title,
                'content': content
            }
        doc_scores[doc_id]['score'] += score * vector_weight
    
    # 排序并归一化分数
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:top_k]
    
    # 归一化分数到 0-1 范围
    results = []
    if sorted_docs:
        max_score = max(info['score'] for _, info in sorted_docs)
        if max_score > 0:
            for doc_id, info in sorted_docs:
                normalized_score = info['score'] / max_score
                results.append((doc_id, normalized_score, info['title'], info['content']))
        else:
            for doc_id, info in sorted_docs:
                results.append((doc_id, info['score'], info['title'], info['content']))
    
    return results
