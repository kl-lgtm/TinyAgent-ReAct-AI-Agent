"""
大模型调用模块
基于官方 tiny-universe/content/TinyAgent/tinyAgent/LLM.py
原版使用 InternLM2 本地模型（需GPU），本版本适配为 DeepSeek API（兼容 CPU）
接口保持完全一致：chat(prompt, history, meta_instruction) -> (response, history)
"""
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class BaseModel:
    """模型基类（与官方一致）"""
    def __init__(self, path: str = '') -> None:
        self.path = path

    def chat(self, prompt: str, history: List[dict], meta_instruction: str = '') -> str:
        pass

    def load_model(self):
        pass


class DeepSeekChat(BaseModel):
    """
    DeepSeek API 调用（替代官方的 InternLM2Chat）
    保持与官方完全相同的 chat() 接口
    """

    def __init__(self, path: str = ''):
        super().__init__(path)
        self.client = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
        )
        self.model_name = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.load_model()

    def load_model(self):
        print(f'================ DeepSeek API 连接成功 (模型: {self.model_name}) ================')

    def chat(self, prompt: str, history: List[Dict], meta_instruction: str = '') -> str:
        """
        调用 DeepSeek API（接口与官方 InternLM2Chat.chat() 完全一致）

        Args:
            prompt: 用户输入文本
            history: 对话历史 [{"role":"user/assistant", "content":"..."}]
            meta_instruction: 系统提示词

        Returns:
            (response, history): 模型回复文本和更新后的历史
        """
        # 构建消息列表
        messages = []
        if meta_instruction:
            messages.append({'role': 'system', 'content': meta_instruction})
        messages.extend(history)
        messages.append({'role': 'user', 'content': prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )
            reply = response.choices[0].message.content

            # 更新历史（与官方行为一致）
            history.append({'role': 'user', 'content': prompt})
            history.append({'role': 'assistant', 'content': reply})

            return reply, history
        except Exception as e:
            print(f'[LLM错误] {e}')
            error_reply = f'Error: {e}'
            history.append({'role': 'user', 'content': prompt})
            history.append({'role': 'assistant', 'content': error_reply})
            return error_reply, history
