"""
Agent 模块 - ReAct 范式智能体
基于官方 tiny-universe/content/TinyAgent/tinyAgent/Agent.py
LLM 后端从 InternLM2 改为 DeepSeek API，并适配消息历史与工具结果回传。
"""
from typing import Dict, List, Optional, Tuple, Union
import json5

# 官方导入 InternLM2Chat，这里改为 DeepSeekChat（接口完全兼容）
from LLM import DeepSeekChat
from tool import Tools


# ============================================================
# System Prompt 模板（与官方完全一致）
# ============================================================
TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""


class Agent:
    """
    基于 ReAct 的 Agent（与官方结构完全一致）
    """

    def __init__(self, path: str = '') -> None:
        self.path = path
        self.tool = Tools()
        self.system_prompt = self.build_system_input()
        # 官方: InternLM2Chat(path)  →  本版本: DeepSeekChat(path)
        self.model = DeepSeekChat(path)

    def build_system_input(self):
        """构建 System Prompt（与官方完全一致）"""
        tool_descs, tool_names = [], []
        for tool in self.tool.toolConfig:
            tool_descs.append(TOOL_DESC.format(**tool))
            tool_names.append(tool['name_for_model'])
        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)
        sys_prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names)
        return sys_prompt

    def parse_latest_plugin_call(self, text):
        """
        解析 LLM 输出中的工具调用（与官方完全一致）
        从 LLM 回复中提取 Action（工具名）和 Action Input（参数）
        """
        plugin_name, plugin_args = '', ''
        # 兼容模型直接以 Action: 开头的输出。
        text = '\n' + text
        i = text.rfind('\nAction:')
        j = text.rfind('\nAction Input:')
        k = text.rfind('\nObservation:')
        if 0 <= i < j:
            if k < j:
                text = text.rstrip() + '\nObservation:'
            k = text.rfind('\nObservation:')
            plugin_name = text[i + len('\nAction:') : j].strip()
            plugin_args = text[j + len('\nAction Input:') : k].strip()
            text = text[:k]
        return plugin_name, plugin_args, text

    def call_plugin(self, plugin_name, plugin_args):
        """
        执行工具调用（与官方完全一致）
        """
        plugin_args = json5.loads(plugin_args)
        if plugin_name == 'google_search':
            return '\nObservation:' + self.tool.google_search(**plugin_args)

    def text_completion(self, text, history=None):
        """
        ReAct 推理入口
        1. LLM 首次推理 → 解析 Action
        2. 执行工具 → 获取 Observation
        3. LLM 二次推理 → 整合结果 → Final Answer
        """
        if history is None:
            history = []
        text = "\nQuestion:" + text
        response, his = self.model.chat(text, history, self.system_prompt)
        print(response)
        plugin_name, plugin_args, _ = self.parse_latest_plugin_call(response)
        if not plugin_name:
            return response, his
        observation = self.call_plugin(plugin_name, plugin_args)
        print(observation)
        # 首次回答已由 LLM.chat 写入历史，只回传真实工具结果。
        response, his = self.model.chat(
            observation.strip() + '\n请根据以上工具结果回答原始问题；如果搜索失败，请如实说明。',
            his, self.system_prompt,
        )
        return response, his


if __name__ == '__main__':
    # 测试 System Prompt 输出
    agent = Agent('')
    prompt = agent.build_system_input()
    print(prompt)
