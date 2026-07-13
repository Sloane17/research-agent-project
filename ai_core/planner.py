# ai_core/planner.py
import json
from ai_core.llm_client import call_llm

def plan_research(query: str):
    """将用户问题拆解为多个可搜索的关键词"""
    prompt = f"""
    你是一个资深学术研究规划师。
    
    用户问题："{query}"
    
    请将这个问题拆解为 3-5 个具体的、可检索的关键词或子问题。
    
    要求：
    1. 关键词要具体，便于搜索
    2. 覆盖问题的不同方面
    3. 只返回 JSON 数组格式
    
    示例输出：["关键词1", "关键词2", "关键词3"]
    """
    
    messages = [{"role": "user", "content": prompt}]
    result = call_llm(messages, temperature=0.3)
    
    if not result:
        return [query]  # 如果失败，返回原问题
    
    try:
        # 清理可能的 Markdown 标记
        clean_result = result.strip().replace("```json", "").replace("```", "")
        keywords = json.loads(clean_result)
        return keywords if isinstance(keywords, list) else [query]
    except:
        # 如果 JSON 解析失败，按逗号分割
        return [q.strip() for q in result.split(",")]