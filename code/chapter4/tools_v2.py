from dotenv import load_dotenv
# 第一行必须先加载env，否则os.getenv读不到
load_dotenv()
import os
import serpapi
from typing import Dict, Any

def search(query: str) -> str:
    """
    基于SerpApi的网页搜索引擎工具，适配新版serpapi库
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 地区中国
            "hl": "zh-cn", # 中文结果
        }
        # 新版 serpapi 调用方式，删除SerpApiClient
        results = serpapi.search(params)
        
        # 智能解析返回内容
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


class ToolExecutor:
    """工具执行器，管理所有可用工具"""
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])


# 测试入口
if __name__ == '__main__':
    toolExecutor = ToolExecutor()
    search_description = "网页搜索引擎，用于查询时事、外部事实类信息"
    toolExecutor.registerTool("Search", search_description, search)
    
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    print("\n--- 执行搜索测试 ---")
    tool_func = toolExecutor.getTool("Search")
    res = tool_func("英伟达最新的GPU型号是什么")
    print("搜索结果：\n", res)