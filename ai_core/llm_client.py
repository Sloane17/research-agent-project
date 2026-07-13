# ai_core/llm_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)

def call_llm(messages, model="deepseek-chat", temperature=0.7):
    """通用的大模型调用函数"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ 调用 LLM 失败: {e}")
        return None

# 测试函数
if __name__ == "__main__":
    result = call_llm([{"role": "user", "content": "你好，请用一句话介绍你自己"}])
    print(result)