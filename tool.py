"""
工具模块 - 基于官方 tiny-universe/content/TinyAgent/tinyAgent/tool.py
原版用 serper API，本版本适配为免费搜索（国内可用）
接口保持完全一致
"""
import json
import requests


class Tools:
    def __init__(self) -> None:
        self.toolConfig = self._tools()

    def _tools(self):
        """工具配置（与官方一致）"""
        tools = [
            {
                'name_for_human': '谷歌搜索',
                'name_for_model': 'google_search',
                'description_for_model': '谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。',
                'parameters': [
                    {
                        'name': 'search_query',
                        'description': '搜索关键词或短语',
                        'required': True,
                        'schema': {'type': 'string'},
                    }
                ],
            }
        ]
        return tools

    def google_search(self, search_query: str) -> str:
        """
        执行网络搜索（多方案兜底，国内可用）
        """
        print(f'  [Tool] 搜索: {search_query}')

        # 方案1：ddgs 库
        result = self._try_ddgs(search_query)
        if result:
            return result

        # 方案2：Bing 搜索
        result = self._try_bing(search_query)
        if result:
            return result

        # 方案3：DuckDuckGo HTML 接口
        result = self._try_ddg_html(search_query)
        if result:
            return result

        # 兜底：返回提示
        return f'关于"{search_query}"的搜索：由于网络限制，当前无法获取实时搜索结果。建议检查网络连接后重试。'

    def _try_ddgs(self, query: str) -> str:
        """尝试 ddgs 库"""
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                if results:
                    formatted = []
                    for i, r in enumerate(results, 1):
                        title = r.get('title', '无标题')
                        body = r.get('body', '')[:300]
                        formatted.append(f'{i}. {title}\n   {body}')
                    return '\n\n'.join(formatted)
        except Exception:
            pass
        return ''

    def _try_bing(self, query: str) -> str:
        """尝试 Bing 搜索"""
        try:
            import urllib.parse
            encoded = urllib.parse.quote(query)
            url = f'https://www.bing.com/search?q={encoded}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            import re
            # 提取搜索结果摘要
            snippets = re.findall(r'<p[^>]*class="b_lineclamp[^"]*"[^>]*>(.*?)</p>', resp.text, re.DOTALL)
            if not snippets:
                snippets = re.findall(r'<span class="b_caption"[^>]*>.*?<p[^>]*>(.*?)</p>', resp.text, re.DOTALL)
            if snippets:
                lines = []
                for i, s in enumerate(snippets[:5], 1):
                    clean = re.sub(r'<[^>]+>', '', s).strip()
                    if len(clean) > 20:
                        lines.append(f'{i}. {clean[:300]}')
                if lines:
                    return '\n\n'.join(lines)
        except Exception:
            pass
        return ''

    def _try_ddg_html(self, query: str) -> str:
        """尝试 DuckDuckGo HTML 接口"""
        try:
            url = 'https://html.duckduckgo.com/html/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.post(url, data={'q': query}, headers=headers, timeout=10)
            import re
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            if snippets:
                lines = []
                for i, s in enumerate(snippets[:5], 1):
                    clean = re.sub(r'<[^>]+>', '', s).strip()
                    lines.append(f'{i}. {clean[:300]}')
                return '\n\n'.join(lines)
        except Exception:
            pass
        return ''
