# ai_core/writer.py
from ai_core.llm_client import call_llm

def write_report(topic: str, raw_data: dict):
    """根据收集到的信息生成结构化报告"""
    
    # 组装上下文
    context = f"# 研究主题: {topic}\n\n"
    for key, value in raw_data.items():
        context += f"## 关于 '{key}'\n{value}\n\n"
    
    prompt = f"""
    你是一个专业的学术报告撰写专家。
    
    请根据以下收集到的信息，撰写一份结构清晰、内容详实的学术研究报告。
    
    {context}
    
    要求：
    1. 使用 Markdown 格式
    2. 包含：标题、摘要、分章节论述、结论
    3. 语言专业、逻辑清晰
    4. 字数在 500-800 字左右
    
    请直接输出 Markdown 格式的报告：
    """
    
    messages = [{"role": "user", "content": prompt}]
    report = call_llm(messages, temperature=0.5)
    
    return report or "生成报告失败，请重试。"