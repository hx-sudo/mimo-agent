import re
import requests
from tools.base import BaseTool


class WebSearch(BaseTool):
    """网页搜索工具，使用百度"""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "搜索网页获取最新信息。当需要查找实时信息、新闻、资料时使用此工具。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词",
                },
            },
            "required": ["query"],
        }

    def execute(self, query: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }

            # Bing 搜索
            resp = requests.get(
                "https://cn.bing.com/search",
                params={"q": query},
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()

            # 解析 Bing 搜索结果
            results = []

            # 提取 h2 标题（Bing 结果在 h2 标签里）
            h2_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL)
            h2_matches = h2_pattern.findall(resp.text)

            for i, h2 in enumerate(h2_matches[:5]):
                clean_title = re.sub(r'<[^>]+>', '', h2).strip()
                if clean_title and clean_title.lower() != "相关搜索":
                    results.append(f"{i+1}. {clean_title}")

            if results:
                return "\n\n".join(results)

            # 备用方案：提取页面文本
            text = re.sub(r'<script[^>]*>.*?</script>', '', resp.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', '\n', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
            content = "\n".join(lines[:15])
            return content if content else f"搜索 '{query}' 未找到结果"

        except Exception as e:
            return f"搜索出错: {e}"
