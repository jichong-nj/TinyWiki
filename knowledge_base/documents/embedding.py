import re
import json
from openai import OpenAI
from typing import List, Tuple, Optional


DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP_SIZE = 100


def split_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap_size: int = DEFAULT_OVERLAP_SIZE) -> List[str]:
    """
    将文本切割成固定大小的片段，带有重叠部分
    
    Args:
        text: 要切割的文本
        chunk_size: 每个片段的大小（字符数）
        overlap_size: 重叠部分的大小（字符数）
    
    Returns:
        切割后的文本片段列表
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        if end < text_length:
            chunk = find_sentence_boundary(text, start, end, overlap_size)
        
        chunks.append(chunk.strip())
        start = start + chunk_size - overlap_size
    
    return chunks


def find_sentence_boundary(text: str, start: int, end: int, overlap_size: int) -> str:
    """
    在指定范围内寻找句子边界，确保切分不会在句子中间断开
    
    Args:
        text: 原始文本
        start: 起始位置
        end: 结束位置
        overlap_size: 重叠大小
    
    Returns:
        调整后的文本片段
    """
    sentence_endings = ['。', '！', '？', '.', '!', '?', '\n\n', '\r\n\r\n']
    
    search_start = max(start, end - overlap_size - 100)
    search_end = min(len(text), end + 50)
    
    best_end = end
    
    for ending in sentence_endings:
        idx = text.rfind(ending, search_start, search_end)
        if idx != -1 and idx > start:
            best_end = idx + len(ending)
            break
    
    return text[start:best_end]


def clean_markdown(text: str) -> str:
    """
    清理 Markdown 格式，保留主要内容
    
    Args:
        text: 原始 Markdown 文本
    
    Returns:
        清理后的纯文本
    """
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'', text)
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def get_embedding(text: str, api_key: str, base_url: str, model_name: str, input_type: str = "query") -> Optional[List[float]]:
    """
    调用 embedding API 获取文本的向量表示
    
    Args:
        text: 要编码的文本
        api_key: API 密钥
        base_url: API 基础地址
        model_name: 模型名称
        input_type: 输入类型（query/document），某些模型需要
    
    Returns:
        向量列表，如果失败返回 None
    """
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print(f"[DEBUG] Embedding request - Base URL: {base_url}")
        print(f"[DEBUG] Embedding request - Model: {model_name}")
        print(f"[DEBUG] Embedding request - Text length: {len(text)} chars")
        print(f"[DEBUG] Embedding request - Input type: {input_type}")
        
        response = client.embeddings.create(
            input=[text],
            model=model_name,
            encoding_format="float",
            extra_body={"input_type": input_type},
            timeout=60.0  # 设置60秒超时
        )
        
        embedding = response.data[0].embedding
        print(f"[DEBUG] Embedding generated - Dimension: {len(embedding)}")
        
        return embedding
    
    except Exception as e:
        print(f"[ERROR] Embedding request failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算两个向量的余弦相似度
    
    Args:
        vec1: 向量1
        vec2: 向量2
    
    Returns:
        余弦相似度值
    """
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def search_chunks(
    query: str,
    chunks: List[Tuple[int, str, str]],
    api_key: str,
    base_url: str,
    model_name: str,
    top_k: int = 5
) -> List[Tuple[int, str, float]]:
    """
    搜索与查询最相似的文档片段
    
    Args:
        query: 查询文本
        chunks: 片段列表，格式为 [(chunk_id, content, embedding_json), ...]
        api_key: API 密钥
        base_url: API 基础地址
        model_name: 模型名称
        top_k: 返回前 k 个结果
    
    Returns:
        匹配结果列表，格式为 [(chunk_id, content, similarity), ...]
    """
    query_embedding = get_embedding(query, api_key, base_url, model_name)
    if query_embedding is None:
        return []
    
    results = []
    
    for chunk_id, content, embedding_json in chunks:
        try:
            chunk_embedding = json.loads(embedding_json)
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            results.append((chunk_id, content, similarity))
        except (json.JSONDecodeError, TypeError):
            continue
    
    results.sort(key=lambda x: x[2], reverse=True)
    
    return results[:top_k]
