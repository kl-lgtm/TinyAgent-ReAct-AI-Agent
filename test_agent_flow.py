"""离线验证对话流程，不调用真实模型或搜索服务。"""
import ast
from pathlib import Path
import unittest


tree = ast.parse(Path(__file__).with_name('Agent.py').read_text(encoding='utf-8'))
agent_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'Agent')
namespace = {}
exec(compile(ast.Module(body=[agent_node], type_ignores=[]), 'Agent.py', 'exec'), namespace)
Agent = namespace['Agent']


class FakeModel:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.prompts = []

    def chat(self, prompt, history, instruction):
        self.prompts.append(prompt)
        reply = next(self.replies, 'Unexpected second request')
        history.extend([{'role': 'user', 'content': prompt},
                        {'role': 'assistant', 'content': reply}])
        return reply, history


class AgentFlowTests(unittest.TestCase):
    def make_agent(self, replies):
        agent = Agent.__new__(Agent)
        agent.model = FakeModel(replies)
        agent.system_prompt = ''
        return agent

    def test_direct_answer_is_returned_without_second_request(self):
        agent = self.make_agent(['Final Answer: hello'])
        response, history = agent.text_completion('hello', [])
        self.assertEqual(response, 'Final Answer: hello')
        self.assertEqual(len(agent.model.prompts), 1)
        self.assertEqual(len(history), 2)

    def test_search_result_is_sent_as_observation(self):
        agent = self.make_agent([
            'Action: google_search\nAction Input: {"search_query":"weather"}',
            'Final Answer: sunny',
        ])
        calls = []
        def search(name, args):
            calls.append((name, args))
            return '\nObservation: sunny'
        agent.call_plugin = search
        response, history = agent.text_completion('search weather', [])
        self.assertEqual(response, 'Final Answer: sunny')
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(agent.model.prompts), 2)
        self.assertTrue(agent.model.prompts[1].startswith('Observation:'))
        self.assertNotIn('Action Input:', agent.model.prompts[1])


if __name__ == '__main__':
    unittest.main()
