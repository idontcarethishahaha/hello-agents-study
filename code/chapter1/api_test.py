# 加载本地.env配置，必须放在最顶部
from dotenv import load_dotenv
import os
load_dotenv()

# 读取环境变量
TAVILY_KEY = os.getenv("TAVILY_API_KEY")
LLM_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL")
LLM_MODEL = os.getenv("MODEL_NAME")

# 简单校验环境变量是否读取成功
print("=== 环境配置读取校验 ===")
print(f"Tavily密钥是否存在: {bool(TAVILY_KEY)}")
print(f"LLM API密钥是否存在: {bool(LLM_API_KEY)}")
print(f"LLM接口地址: {LLM_BASE_URL}")
print(f"LLM模型名称: {LLM_MODEL}\n")

# ---------------------- 测试天气API ----------------------
import requests
print("=== 天气API测试 ===")
try:
    response = requests.get("https://wttr.in/Beijing?format=j1", timeout=10)
    print("天气API状态码:", response.status_code)
    if response.status_code == 200:
        print("天气接口连接正常\n")
    else:
        print("天气接口访问异常\n")
except Exception as e:
    print("天气接口请求出错：", e, "\n")

# ---------------------- 测试 Tavily API ----------------------
from tavily import TavilyClient
print("=== Tavily 搜索API测试 ===")
if not TAVILY_KEY:
    print("错误：未读取到.env中的TAVILY_API_KEY")
else:
    tavily = TavilyClient(api_key=TAVILY_KEY)
    try:
        result = tavily.search("北京晴天适合去哪玩", search_depth="basic")
        ans = result.get("answer")
        if ans and len(ans.strip()) > 0:
            print("Tavily API 连接成功，返回摘要：", ans[:50])
        else:
            res_list = result.get("results", [])
            if res_list and len(res_list) > 0:
                title = res_list[0].get("title", "无标题")
                print("Tavily API 连接成功，第一条结果标题：", title)
            else:
                print("Tavily搜索无有效内容返回")
    except Exception as e:
        print("Tavily API 错误:", e)
print()

# ---------------------- 测试智谱GLM LLM API ----------------------
from openai import OpenAI
print("=== LLM大模型API测试 ===")
if not all([LLM_API_KEY, LLM_BASE_URL, LLM_MODEL]):
    print("错误：LLM相关环境变量缺失，请检查.env")
else:
    client = OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL
    )
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是友好的AI助手，简短回答用户问题"},
                {"role": "user", "content": "你好，简单介绍下你自己"}
            ],
            max_tokens=200,
            timeout=15
        )
        content = response.choices[0].message.content.strip()
        if content:
            print("LLM API 连接成功，返回内容:", content)
        else:
            print("LLM API 连接成功，但模型返回空文本")
    except Exception as e:
        print("LLM API 错误:", e)