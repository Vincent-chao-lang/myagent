"""知识提取模块"""

import re
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger


class KnowledgeExtractor:
    """知识提取器"""

    def __init__(self, llm):
        """
        初始化知识提取器

        Args:
            llm: LLM实例
        """
        self.llm = llm
        self.logger = logger

    async def extract_all(self, parsed_contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从所有解析内容中提取知识

        Args:
            parsed_contents: 解析后的内容列表

        Returns:
            提取的知识列表
        """
        learnings = []

        # 过滤掉空内容
        valid_contents = [
            c for c in parsed_contents
            if c.get("content") and len(c.get("content", "")) > 50
        ]

        self.logger.info(f"开始从 {len(valid_contents)} 条内容中提取知识")

        # 加载提示词模板
        prompt_template = self._load_prompt_template()

        for content in valid_contents[:20]:  # 限制处理数量
            try:
                learning = await self.extract_knowledge(content, prompt_template)
                if learning and self._is_valid_learning(learning):
                    learnings.append(learning)
            except Exception as e:
                self.logger.warning(f"提取知识失败 {content.get('title', '')}: {e}")

        self.logger.info(f"成功提取 {len(learnings)} 条有价值的知识")
        return learnings

    async def extract_knowledge(
        self,
        content: Dict[str, Any],
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        从单个内容中提取知识

        Args:
            content: 解析后的内容
            prompt_template: 提示词模板

        Returns:
            提取的知识
        """
        # 跳过过短的内容
        text_content = content.get("content", "")
        if len(text_content) < 100:
            return None

        # 构建提示词
        prompt = prompt_template.format(
            title=content.get("title", ""),
            content=text_content[:4000],  # 限制长度
            url=content.get("url", "")
        )

        messages = [
            {"role": "system", "content": "你是一个Python知识提取专家，擅长从技术文章中提取核心知识点。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 调用LLM
            response = await self.llm.achat(messages)

            # 解析响应
            learning = self._parse_structured_response(response, content)

            return learning

        except Exception as e:
            self.logger.error(f"LLM提取失败: {e}")
            # 降级：直接使用原始内容
            return self._create_fallback_learning(content)

    def _parse_structured_response(self, response: str, original_content: Dict[str, Any]) -> Dict[str, Any]:
        """解析LLM的结构化响应"""
        try:
            # 尝试解析结构化输出
            title = self._extract_field(response, "标题") or original_content.get("title", "")
            category = self._extract_field(response, "类别") or "concept"
            core_content = self._extract_field(response, "核心内容") or response
            code_example = self._extract_field(response, "代码示例") or ""
            tags = self._extract_field(response, "相关标签") or ""
            importance = self._extract_field(response, "重要性") or "3"

            # 处理标签
            tag_list = [t.strip() for t in tags.replace("、", ",").split(",") if t.strip()]

            # 如果没有提取到有效标签，从内容中推断
            if not tag_list:
                tag_list = self._infer_tags_from_content(core_content)

            # 清理代码示例
            if code_example and code_example != "无":
                code_example = self._extract_code_block(response)
            else:
                code_example = self._extract_code_from_content(original_content.get("content", ""))

            return {
                "title": title,
                "content": core_content,
                "category": category,
                "tags": tag_list,
                "code_example": code_example,
                "source": original_content.get("source", ""),
                "importance": int(importance) if importance.isdigit() else 3,
                "url": original_content.get("url", "")
            }

        except Exception as e:
            self.logger.warning(f"解析结构化响应失败: {e}")
            return self._create_fallback_learning(original_content)

    def _extract_field(self, text: str, field_name: str) -> str:
        """从文本中提取字段"""
        patterns = [
            rf'\*\*{field_name}\*\*:\s*([^\n]+)',
            rf'{field_name}[:：]\s*([^\n]+)',
            rf'【{field_name}】[:：]\s*([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_code_block(self, text: str) -> str:
        """提取代码块"""
        # 提取python代码块
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return "\n\n".join(matches)

        # 尝试提取任何代码块
        pattern = r'```\n?(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return "\n\n".join(matches)

        return ""

    def _extract_code_from_content(self, content: str) -> str:
        """从原始内容中提取代码"""
        # 简单的代码提取
        code_pattern = r'```python\n(.*?)```'
        matches = re.findall(code_pattern, content, re.DOTALL)

        if matches:
            return matches[0]

        return ""

    def _infer_tags_from_content(self, content: str) -> List[str]:
        """从内容推断标签"""
        tech_tags = {
            "async": ["async", "await", "asyncio", "coroutine", "并发", "异步"],
            "type-hints": ["type", "hint", "typing", "类型", "注解"],
            "fastapi": ["fastapi", "api", "web", "框架"],
            "django": ["django", "web", "框架"],
            "flask": ["flask", "micro", "framework"],
            "pytest": ["pytest", "test", "testing", "测试"],
            "dataclass": ["dataclass", "data", "类"],
            "decorator": ["decorator", "装饰器", "@", "wrapper"],
            "generator": ["generator", "yield", "生成器"],
            "context-manager": ["context", "manager", "with", "__enter__", "__exit__"],
            "performance": ["performance", "optimization", "optimize", "性能", "优化"],
            "pattern": ["pattern", "设计模式", "singleton", "factory", "observer"],
        }

        content_lower = content.lower()
        found_tags = []

        for tag, keywords in tech_tags.items():
            if any(kw in content_lower for kw in keywords):
                found_tags.append(tag)

        return found_tags[:5] if found_tags else ["python"]

    def _create_fallback_learning(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """创建降级学习条目"""
        text = content.get("content", "")[:500]

        return {
            "title": content.get("title", ""),
            "content": text,
            "category": "general",
            "tags": ["python"],
            "code_example": "",
            "source": content.get("source", ""),
            "importance": 2,
            "url": content.get("url", "")
        }

    def _is_valid_learning(self, learning: Dict[str, Any]) -> bool:
        """验证学习条目是否有效"""
        # 检查是否有实质内容
        content = learning.get("content", "")
        if len(content) < 50:
            return False

        # 检查是否是无效响应
        invalid_patterns = [
            "没有提供内容",
            "请提供",
            "无法提取",
            "为空"
        ]

        for pattern in invalid_patterns:
            if pattern in content:
                return False

        return True

    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "knowledge_extraction.md"

        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        # 默认模板
        return """请从以下内容中提取有价值的Python相关知识：

标题：{title}

内容：
{content}

来源：{url}

请提取：
1. 核心概念和知识点（100-300字）
2. 代码示例（如果有，完整提取）
3. 最佳实践建议

用结构化的方式输出，包含：标题、类别、核心内容、代码示例、相关标签。
"""
