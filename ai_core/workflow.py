# ai_core/workflow.py
from ai_core.planner import plan_research
from ai_core.searcher import gather_information
from ai_core.writer import write_report

def run_research_workflow_stream(user_query: str):
    """流式执行研究工作流，每一步都 yield 状态"""
    
    yield {"type": "status", "message": f"📝 开始研究: {user_query}"}
    
    # 步骤 1: 规划
    yield {"type": "status", "message": "🔧 步骤 1/3: 拆解问题..."}
    keywords = plan_research(user_query)
    yield {"type": "status", "message": f"   ✅ 生成关键词: {', '.join(keywords)}"}
    
    # 步骤 2: 搜集
    yield {"type": "status", "message": "🔍 步骤 2/3: 搜集资料..."}
    raw_info = {}
    for i, kw in enumerate(keywords):
        yield {"type": "status", "message": f"   🔍 正在搜索: {kw} ({i+1}/{len(keywords)})"}
        from ai_core.searcher import search_wikipedia
        result = search_wikipedia(kw)
        raw_info[kw] = result
    yield {"type": "status", "message": f"   ✅ 搜集到 {len(raw_info)} 个来源的信息"}
    
    # 步骤 3: 生成报告
    yield {"type": "status", "message": "✍️ 步骤 3/3: 生成报告..."}
    report = write_report(user_query, raw_info)
    yield {"type": "status", "message": "   ✅ 报告生成完成！"}
    
    # 返回最终结果
    yield {"type": "result", "content": report}

# ai_core/workflow.py

def run_research_workflow(user_query: str):
    """非流式版本 - 直接返回最终报告"""
    
    print(f"📝 开始研究: {user_query}")
    
    # 步骤 1: 规划
    print("🔧 步骤 1/3: 拆解问题...")
    keywords = plan_research(user_query)
    print(f"   ✅ 生成关键词: {', '.join(keywords)}")
    
    # 步骤 2: 搜集
    print("🔍 步骤 2/3: 搜集资料...")
    raw_info = {}
    for i, kw in enumerate(keywords):
        print(f"   🔍 正在搜索: {kw} ({i+1}/{len(keywords)})")
        from ai_core.searcher import search_wikipedia
        result = search_wikipedia(kw)
        raw_info[kw] = result
    print(f"   ✅ 搜集到 {len(raw_info)} 个来源的信息")
    
    # 步骤 3: 生成报告
    print("✍️ 步骤 3/3: 生成报告...")
    report = write_report(user_query, raw_info)
    print("   ✅ 报告生成完成！")
    
    return report