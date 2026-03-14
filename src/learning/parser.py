"""内容解析模块"""

import asyncio
import aiohttp
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from loguru import logger
import re


class ContentParser:
    """内容解析器"""

    def __init__(self):
        self.session = None
        self.logger = logger

    async def parse_all(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解析所有搜索结果

        Args:
            search_results: 搜索结果列表

        Returns:
            解析后的内容列表
        """
        parsed_contents = []

        # 限制并发数
        semaphore = asyncio.Semaphore(5)

        async def parse_with_semaphore(result):
            async with semaphore:
                return await self.parse_content(result)

        tasks = [parse_with_semaphore(r) for r in search_results]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                self.logger.warning(f"解析失败: {result}")
            elif result:
                parsed_contents.append(result)

        return parsed_contents

    async def parse_content(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单个内容

        Args:
            result: 搜索结果

        Returns:
            解析后的内容
        """
        url = result.get("url", "")
        title = result.get("title", "")
        source = result.get("source", "")

        try:
            # 获取内容
            content = await self._fetch_url(url)

            if not content:
                return None

            # 提取主要内容
            parsed = self._extract_main_content(content, url)

            return {
                "url": url,
                "title": title or parsed.get("title", ""),
                "content": parsed.get("content", ""),
                "source": source,
                "author": parsed.get("author", ""),
                "date": parsed.get("date", ""),
                "tags": parsed.get("tags", [])
            }

        except Exception as e:
            self.logger.error(f"解析内容失败 {url}: {e}")
            return None

    async def _fetch_url(self, url: str) -> str:
        """获取URL内容"""
        if not url.startswith(("http://", "https://")):
            return ""

        try:
            if self.session is None or self.session.closed:
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()

        except Exception as e:
            self.logger.debug(f"获取URL失败 {url}: {e}")

        return ""

    def _extract_main_content(self, html: str, url: str) -> Dict[str, Any]:
        """提取主要内容"""
        soup = BeautifulSoup(html, "html.parser")

        # 移除不需要的标签
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # 提取标题
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()

        # 尝试找文章主体
        article = soup.find("article")
        if not article:
            article = soup.find("div", class_=re.compile(r"(post|content|article|entry)", re.I))
        if not article:
            article = soup.find("main")

        if article:
            # 转换为Markdown
            content = md(str(article))
        else:
            # 降级：获取所有段落
            paragraphs = soup.find_all("p")
            content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        # 清理内容
        content = self._clean_content(content)

        # 提取元数据
        author = self._extract_author(soup)
        date = self._extract_date(soup)
        tags = self._extract_tags(soup)

        return {
            "title": title,
            "content": content,
            "author": author,
            "date": date,
            "tags": tags
        }

    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除过多的空行
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 移除HTML实体
        content = re.sub(r'&[a-z]+;', '', content)

        return content.strip()

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者"""
        for meta in soup.find_all("meta"):
            if meta.get("name", "").lower() in ["author", "dc.creator"]:
                return meta.get("content", "")

        for tag in soup.find_all(class_=re.compile(r"author", re.I)):
            return tag.get_text().strip()

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """提取日期"""
        for meta in soup.find_all("meta"):
            if meta.get("property", "").lower() in ["article:published_time", "dc.date"]:
                return meta.get("content", "")

        for tag in soup.find_all(["time", "span"], class_=re.compile(r"date|time", re.I)):
            return tag.get_text().strip()

        return ""

    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """提取标签"""
        tags = []

        for tag in soup.find_all(["a", "span"], class_=re.compile(r"tag|category", re.I)):
            tag_text = tag.get_text().strip()
            if tag_text and len(tag_text) < 50:
                tags.append(tag_text)

        return tags[:10]

    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
