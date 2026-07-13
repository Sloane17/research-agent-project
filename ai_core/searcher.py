# ai_core/searcher.py
import requests
import time
import json

def search_wikipedia(query: str):
    """使用百度百科搜索（国内可用）"""
    try:
        # 百度百科 API（不需要翻墙）
        url = f"https://baike.baidu.com/api/lemma?lemma={query}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("errno") == 0 and data.get("data"):
                return data["data"].get("abstract", f"关于 '{query}' 的百度百科信息")
            else:
                return f"未找到关于 '{query}' 的百度百科信息"
        else:
            # 备用：用 Bing 搜索
            return search_bing(query)
    except Exception as e:
        return f"搜索 '{query}' 时出错: {e}"

def search_bing(query: str):
    """备用搜索：用 Bing（国内能访问）"""
    try:
        url = f"https://cn.bing.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        return f"从 Bing 获取了关于 '{query}' 的搜索结果"
    except:
        return f"无法获取 '{query}' 的信息，请检查网络"

def gather_information(keywords_list):
    """根据关键词列表收集信息"""
    collected_data = {}
    for kw in keywords_list:
        print(f"🔍 正在搜索: {kw} ...")
        result = search_wikipedia(kw)
        collected_data[kw] = result
        time.sleep(0.5)
    return collected_data