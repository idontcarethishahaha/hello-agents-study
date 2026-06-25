import os
import ast
from llm_client_test import HelloAgentsLLM
from dotenv import load_dotenv
from typing import List, Dict

try:
    load_dotenv()
except FileNotFoundError:
    print("警告：未找到 .env 文件，将使用系统环境变量。")
except Exception as e:
    print(f"警告：加载 .env 文件时出错: {e}")

PLANNER_PROMPT_TEMPLATE = """
你是顶级AI任务规划专家。请把用户复杂问题拆分为有序、独立、可依次执行的简单子步骤。
每一步仅描述单一任务，严格遵循输出格式，只返回指定python列表，不要多余文字。

用户问题: {question}

强制输出格式，前后```python 和 ```不能省略：
```python
["步骤1文字描述", "步骤2文字描述", "步骤3文字描述"]
"""
class Planner:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def plan(self, question: str) -> List[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        print("--- 正在生成分步行动计划 ---")
        response_text = self.llm_client.think(messages=messages) or ""
        print(f"✅ 模型输出原始计划:\n {response_text}")
        try:
            plan_code_block = response_text.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_code_block)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 计划列表解析失败: {e}")
            print(f"模型原始返回内容：{response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划发生未知错误: {e}")
            return []
EXECUTOR_PROMPT_TEMPLATE = """
你是专业任务执行助手，仅专注完成【当前步骤】，只输出该步骤计算 / 推理结果，禁止额外解释、闲聊。
原始总问题：{question}
完整分步计划：{plan}
已完成步骤历史记录：{history}
现在需要执行的当前步骤：{current_step}
只输出当前步骤的答案，不要任何多余文字：
"""
class Executor:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> str:
        history = ""
        final_answer = ""
        print("\n--- 开始逐条执行计划步骤 ---")
        total_step = len(plan)
        for idx, step in enumerate(plan, 1):
            print(f"\n===== 执行步骤 {idx}/{total_step}：{step} =====")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "暂无已完成步骤",
                current_step=step
            )
            messages = [{"role": "user", "content": prompt}]
            step_result = self.llm_client.think(messages=messages) or ""
            history += f"步骤 {idx}：{step}\n 该步骤结果：{step_result}\n\n"
            final_answer = step_result
            print(f"✅ 步骤 {idx} 执行完成，结果：{step_result}")
        return final_answer
class PlanAndSolveAgent:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        print(f"\n========== 启动规划求解智能体 ==========\n 用户总问题：{question}")
        task_plan = self.planner.plan(question)
        if not task_plan:
            print("\n❌ 无法生成合法分步计划，任务终止")
            return
        print(f"\n✅ 生成完整任务计划：{task_plan}")
        final_output = self.executor.execute(question, task_plan)
        print(f"\n========== 全部任务执行完毕 ==========\n 最终汇总答案：{final_output}")


if __name__ == '__main__':
    try:
        llm_client = HelloAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        test_question = "一个水果店周一卖出了 15 个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了 5 个。请问这三天总共卖出了多少个苹果？"
        agent.run(test_question)
    except ValueError as err:
        print(f"初始化 LLM 客户端失败：{err}")