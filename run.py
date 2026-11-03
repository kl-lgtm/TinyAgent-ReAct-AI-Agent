"""
TinyAgent 实验入口（基于官方 agent_demo.ipynb 测试流程）
"""
import sys
import io
# 修复 Windows 终端 GBK 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from Agent import Agent


if __name__ == '__main__':
    # 初始化 Agent
    agent = Agent('')

    # 打印 System Prompt
    print("\n" + "=" * 60)
    print("  System Prompt（注入 LLM 的工具描述和输出格式）")
    print("=" * 60)
    print(agent.system_prompt)

    # 测试 1：简单对话
    print("\n" + "=" * 60)
    print("  测试 1：简单对话")
    print("=" * 60)
    response, history = agent.text_completion(text='你好', history=[])
    print(f"\n>>> 最终响应:\n{response}")

    # 测试 2：实时信息查询
    print("\n" + "=" * 60)
    print("  测试 2：实时信息查询")
    print("=" * 60)
    response, history = agent.text_completion(
        text='请务必调用 google_search 工具，搜索北京今天的天气，并根据真实搜索结果回答；如果搜索失败请如实说明。',
        history=history
    )
    print(f"\n>>> 最终响应:\n{response}")

    # 测试 3：人物查询
    print("\n" + "=" * 60)
    print("  测试 3：人物信息查询")
    print("=" * 60)
    response, history = agent.text_completion(
        text='周杰伦是谁？',
        history=history
    )
    print(f"\n>>> 最终响应:\n{response}")

    # 测试 4：上下文联系查询
    print("\n" + "=" * 60)
    print("  测试 4：上下文关联查询")
    print("=" * 60)
    response, history = agent.text_completion(
        text='他的第一张专辑是什么？',
        history=history
    )
    print(f"\n>>> 最终响应:\n{response}")



