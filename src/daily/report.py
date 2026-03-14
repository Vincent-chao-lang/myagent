"""日报生成模块"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger


class DailyReportGenerator:
    """每日日报生成器"""

    def __init__(self, knowledge_store, skill_tracker, config):
        """
        初始化日报生成器

        Args:
            knowledge_store: 知识库实例
            skill_tracker: 技能追踪器
            config: 配置对象
        """
        self.knowledge_store = knowledge_store
        self.skill_tracker = skill_tracker
        self.config = config

        self.logger = logger

    def format_duration(self, seconds: float) -> str:
        """
        格式化时长为可读字符串

        Args:
            seconds: 秒数

        Returns:
            格式化的时长字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            return f"{int(hours)}小时{int(minutes)}分钟"

    async def generate(self, learnings: List[Dict[str, Any]], learning_stats: Dict[str, Any] = None) -> str:
        """
        生成每日学习日报

        Args:
            learnings: 学习内容列表
            learning_stats: 学习统计信息（包含时长）

        Returns:
            日报内容
        """
        date = datetime.now()

        # 统计信息
        stats = self._calculate_stats(learnings)

        # 核心知识
        core_knowledge = self._extract_core_knowledge(learnings)

        # 代码示例
        code_examples = self._extract_code_examples(learnings)

        # 技能更新
        skill_updates = self._format_skill_updates()

        # 标签云
        tag_cloud = self._format_tag_cloud()

        # 学习来源
        sources = self._format_sources(learnings)

        # 学习时长信息
        if learning_stats and "stage_times" in learning_stats:
            stage_times = learning_stats["stage_times"]
            total_time = learning_stats.get("total_time", 0)

            learning_duration = self.format_duration(total_time)
            search_time = self.format_duration(stage_times.get("search", 0))
            parse_time = self.format_duration(stage_times.get("parse", 0))
            extract_time = self.format_duration(stage_times.get("extract", 0))
            total_time_formatted = self.format_duration(total_time)
        else:
            learning_duration = "未记录"
            search_time = "未记录"
            parse_time = "未记录"
            extract_time = "未记录"
            total_time_formatted = "未记录"

        # 加载模板
        template = self._load_template()

        # 填充模板
        report = template.format(
            date=date.strftime("%Y-%m-%d"),
            timestamp=date.strftime("%Y-%m-%d %H:%M:%S"),
            total_count=stats["total"],
            new_skills=stats["new_skills"],
            code_count=stats["code_examples"],
            learning_duration=learning_duration,
            search_time=search_time,
            parse_time=parse_time,
            extract_time=extract_time,
            total_time=total_time_formatted,
            core_knowledge=core_knowledge,
            code_examples=code_examples,
            skill_updates=skill_updates,
            skill_cloud=tag_cloud,
            new_docs=stats.get("new_docs", 0),
            updated_docs=stats.get("updated_docs", 0),
            sources=sources
        )

        return report

    def _calculate_stats(self, learnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {
            "total": len(learnings),
            "new_skills": 0,
            "code_examples": 0,
            "new_docs": 0,
            "updated_docs": 0
        }

        categories = set()
        sources = set()

        for learning in learnings:
            category = learning.get("category", "")
            if category:
                categories.add(category)

            source = learning.get("source", "")
            if source:
                sources.add(source)

            # 检查代码示例
            content = learning.get("content", "")
            if "```" in content or "code" in content.lower():
                stats["code_examples"] += 1

        stats["categories"] = len(categories)
        stats["sources"] = len(sources)

        # 从技能追踪器获取新技能数
        recent_skills = self.skill_tracker.get_top_skills(5)
        stats["new_skills"] = len(recent_skills)

        return stats

    def _extract_core_knowledge(self, learnings: List[Dict[str, Any]]) -> str:
        """提取核心知识"""
        sections = []

        # 按类别分组
        by_category = {}
        for learning in learnings:
            cat = learning.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(learning)

        # 格式化每个类别
        for category, items in by_category.items():
            if not items:
                continue

            section = f"\n### {category.title()}\n\n"

            for item in items[:5]:  # 每个类别最多5条
                title = item.get("title", "")
                content = item.get("content", "")[:200]

                section += f"**{title}**\n"
                section += f"{content}...\n\n"

            sections.append(section)

        return "\n".join(sections)

    def _extract_code_examples(self, learnings: List[Dict[str, Any]]) -> str:
        """提取代码示例"""
        examples = []

        for learning in learnings:
            content = learning.get("content", "")

            # 提取代码块
            if "```python" in content:
                # 提取Python代码块
                start = content.find("```python")
                end = content.find("```", start + 9)
                if end > start:
                    code = content[start + 9:end].strip()
                    title = learning.get("title", "代码示例")

                    examples.append(f"#### {title}\n\n```python\n{code}\n```")
                    if len(examples) >= 5:  # 最多5个示例
                        break

        return "\n\n".join(examples) if examples else "无代码示例"

    def _format_skill_updates(self) -> str:
        """格式化技能更新"""
        top_skills = self.skill_tracker.get_top_skills(10)

        lines = []
        for skill in top_skills:
            lines.append(f"- **{skill.name}**: {skill.mentions} 次提及")

        return "\n".join(lines)

    def _format_tag_cloud(self) -> str:
        """格式化标签云"""
        tag_cloud = self.skill_tracker.get_tag_cloud(30)

        # 简单格式化
        tags = []
        for name, count in tag_cloud:
            # 根据次数添加符号表示热度
            heat = "🔥" * min(count // 5 + 1, 5)
            tags.append(f"{name} {heat}")

        return " ".join(tags)

    def _format_sources(self, learnings: List[Dict[str, Any]]) -> str:
        """格式化学习来源"""
        source_counts = {}

        for learning in learnings:
            source = learning.get("source", "未知")
            source_counts[source] = source_counts.get(source, 0) + 1

        lines = []
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {source}: {count} 条")

        return "\n".join(lines)

    def _load_template(self) -> str:
        """加载日报模板"""
        template_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "daily_report.md"

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()

        # 默认模板
        return """# 每日学习日报 - {date}

## 📊 学习统计

- **学习条目**: {total_count}
- **新增技能**: {new_skills}
- **代码示例**: {code_count}
- **学习时长**: {learning_duration}

## ⏱️ 学习用时分析

- **网络搜索**: {search_time}
- **内容解析**: {parse_time}
- **知识提取**: {extract_time}
- **总计用时**: {total_time}

## 📚 今日学习内容

### 核心知识点

{core_knowledge}

### 代码示例

{code_examples}

### 技能更新

{skill_updates}

## 🎯 技能标签云

{skill_cloud}

## 🔗 学习来源

{sources}

---

*由PyAgent自动生成于 {timestamp}*
"""
