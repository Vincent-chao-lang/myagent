"""网络搜索模块"""

import asyncio
import aiohttp
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from feedparser import parse as parse_feed
from loguru import logger


class WebSearcher:
    """网络搜索器"""

    def __init__(self, config):
        """
        初始化网络搜索器

        Args:
            config: 配置对象
        """
        self.config = config
        self.sources = config.learning_sources
        self.search_queries = config.search_queries
        self.session = None
        self.logger = logger

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=60)  # 增加超时时间
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def search_all(self) -> List[Dict[str, Any]]:
        """
        执行所有搜索任务

        Returns:
            搜索结果列表
        """
        all_results = []

        # 搜索各个来源
        for source in self.sources:
            try:
                results = await self._search_source(source)
                all_results.extend(results)
                self.logger.info(f"从 {source.get('name', source.get('type'))} 获取 {len(results)} 条结果")
            except Exception as e:
                self.logger.error(f"搜索 {source.get('name')} 失败: {e}")

        return all_results

    async def _search_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        搜索单个来源

        Args:
            source: 来源配置

        Returns:
            搜索结果列表
        """
        source_type = source.get("type", "").lower()

        if source_type == "blog":
            return await self._fetch_blog(source)
        elif source_type == "github":
            return await self._fetch_github_trending(source)
        elif source_type == "news":
            return await self._fetch_hacker_news(source)
        elif source_type == "pypi":
            return await self._fetch_pypi(source)
        elif source_type == "rss":
            return await self._fetch_rss(source)
        else:
            self.logger.warning(f"不支持的来源类型: {source_type}")
            return []

    async def _fetch_blog(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """抓取博客"""
        results = []
        url = source.get("url", "")

        try:
            session = await self._get_session()

            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"博客访问失败 {url}: {response.status}")
                    return []

                html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            # 提取文章链接
            articles = []
            for tag in soup.find_all(["article", "div"], class_=["post", "entry", "article"]):
                link = tag.find("a", href=True)
                if link:
                    href = link["href"]
                    title = link.get_text().strip()
                    if title and href:
                        # 处理相对链接
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = url.rstrip("/") + href
                            else:
                                href = url.rstrip("/") + "/" + href
                        articles.append({
                            "url": href,
                            "title": title,
                            "source": source.get("name", url)
                        })

            # 限制数量并获取实际内容
            for article in articles[:10]:
                try:
                    content = await self._fetch_and_extract_content(article["url"])
                    if content:
                        article.update(content)
                        results.append(article)
                except Exception as e:
                    self.logger.debug(f"获取文章内容失败 {article['url']}: {e}")

        except Exception as e:
            self.logger.error(f"抓取博客失败 {url}: {e}")

        return results

    async def _fetch_and_extract_content(self, url: str) -> Dict[str, Any]:
        """获取并提取网页内容"""
        try:
            session = await self._get_session()

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    return {}

                html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            # 移除不需要的标签
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                tag.decompose()

            # 提取主要内容
            article = soup.find("article")
            if not article:
                article = soup.find("div", class_=lambda x: x and any(
                    term in str(x.get("class", "")).lower() for term in ["post", "content", "article", "entry", "main"]
                ))

            if article:
                from markdownify import markdownify as md
                content = md(str(article))
            else:
                # 降级：获取段落
                paragraphs = soup.find_all(["p", "pre", "code"])
                content = "\n\n".join([tag.get_text().strip() for tag in paragraphs if tag.get_text().strip()])

            # 清理内容
            import re
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()

            if len(content) > 100:
                return {"content": content}

        except Exception as e:
            self.logger.debug(f"提取内容失败 {url}: {e}")

        return {}

    async def _fetch_github_trending(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取GitHub趋势"""
        results = []

        try:
            session = await self._get_session()
            query = source.get("query", "language:python")

            async with session.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": 10}
            ) as response:
                if response.status != 200:
                    return []

                data = await response.json()

            for item in data.get("items", []):
                # 获取README内容
                readme_url = f"https://raw.githubusercontent.com/{item['full_name']}/main/README.md"
                readme_content = await self._fetch_github_readme(readme_url)

                results.append({
                    "url": item["html_url"],
                    "title": item["name"],
                    "description": item.get("description", ""),
                    "content": readme_content or item.get("description", ""),
                    "source": "GitHub Trending",
                    "stars": item.get("stargazers_count", 0)
                })

        except Exception as e:
            self.logger.error(f"获取GitHub趋势失败: {e}")

        return results

    async def _fetch_github_readme(self, readme_url: str) -> str:
        """获取GitHub README"""
        try:
            session = await self._get_session()
            async with session.get(readme_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    return await response.text()
        except Exception:
            pass
        return ""

    async def _fetch_hacker_news(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取Hacker News"""
        results = []

        try:
            session = await self._get_session()

            async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as response:
                if response.status != 200:
                    return []

                story_ids = await response.json()

            # 获取前20条
            for story_id in story_ids[:20]:
                try:
                    async with session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") as response:
                        if response.status != 200:
                            continue

                        story = await response.json()

                    # 过滤Python相关
                    title = story.get("title", "").lower()
                    if any(keyword in title for keyword in ["python", "django", "flask", "fastapi", "async", "pypi"]):
                        # 获取URL内容
                        url = story.get("url", "")
                        if url:
                            content = await self._fetch_and_extract_content(url)
                            results.append({
                                "url": url,
                                "title": story.get("title", ""),
                                "content": content.get("content", ""),
                                "source": "Hacker News"
                            })
                        else:
                            results.append({
                                "url": f"https://news.ycombinator.com/item?id={story_id}",
                                "title": story.get("title", ""),
                                "content": "",
                                "source": "Hacker News"
                            })

                except Exception:
                    continue

        except Exception as e:
            self.logger.error(f"获取Hacker News失败: {e}")

        return results

    async def _fetch_pypi(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取PyPI新包（优化版，获取实际内容）"""
        results = []

        try:
            session = await self._get_session()

            # 获取PyPI RSS
            async with session.get("https://pypi.org/rss/packages.xml") as response:
                if response.status != 200:
                    return []

                rss_content = await response.text()

            feed = parse_feed(rss_content)

            # 只处理热门包
            filter_popular = source.get("filter_popular", False)

            for entry in feed.entries[:20]:
                package_name = entry.title.split(" ")[0]

                # 如果开启过滤，跳过不常见的包
                if filter_popular:
                    # 这里可以添加热门包的判断逻辑
                    pass

                # 获取包的详细页面和README
                package_url = entry.link
                content = await self._fetch_pypi_package(package_url)

                results.append({
                    "url": package_url,
                    "title": package_name,
                    "description": entry.get("description", ""),
                    "content": content,
                    "source": "PyPI",
                    "version": entry.get("title", "")
                })

        except Exception as e:
            self.logger.error(f"获取PyPI失败: {e}")

        return results

    async def _fetch_pypi_package(self, package_url: str) -> str:
        """获取PyPI包的详细内容"""
        try:
            session = await self._get_session()

            # 添加项目页面URL
            project_url = package_url.replace("/project/", "/")

            async with session.get(project_url, headers={
                "User-Agent": "Mozilla/5.0"
            }) as response:
                if response.status != 200:
                    return ""

                html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            # 提取项目描述
            description_elem = soup.find("meta", attrs={"name": "description"})
            description = description_elem.get("content", "") if description_elem else ""

            # 提取README内容
            readme_section = soup.find("div", class_="project-description")
            if readme_section:
                # 获取README链接
                readme_link = soup.find("a", string="GitHub")
                if readme_link:
                    readme_url = readme_link["href"]
                    readme_content = await self._fetch_github_readme(readme_url)
                    if readme_content:
                        return f"{description}\n\n{readme_content[:5000]}"

            return description

        except Exception as e:
            self.logger.debug(f"获取PyPI包详情失败: {e}")
            return ""

    async def _fetch_rss(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取RSS订阅"""
        results = []

        try:
            session = await self._get_session()

            async with session.get(source.get("url", "")) as response:
                if response.status != 200:
                    return []

                rss_content = await response.text()

            feed = parse_feed(rss_content)

            for entry in feed.entries[:10]:
                # 获取文章内容
                content = ""
                if entry.link:
                    extracted = await self._fetch_and_extract_content(entry.link)
                    content = extracted.get("content", "")

                results.append({
                    "url": entry.get("link", ""),
                    "title": entry.get("title", ""),
                    "description": entry.get("description", ""),
                    "content": content,
                    "source": source.get("name", "RSS"),
                    "date": entry.get("published", "")
                })

        except Exception as e:
            self.logger.error(f"获取RSS失败: {e}")

        return results

    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
