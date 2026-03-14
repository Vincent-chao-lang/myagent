"""技能追踪模块"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import Counter
from loguru import logger
from dataclasses import dataclass, field, asdict


@dataclass
class Skill:
    """技能条目"""
    name: str
    mentions: int = 0
    last_practiced: str = ""
    related_concepts: List[str] = field(default_factory=list)
    category: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class SkillTracker:
    """技能追踪器"""

    def __init__(self, storage_path: Path = None):
        """
        初始化技能追踪器

        Args:
            storage_path: 存储路径
        """
        if storage_path is None:
            storage_path = Path("./data/skills.json")

        self.storage_path = Path(storage_path).absolute()
        self.skills: Dict[str, Skill] = {}
        self.history: List[Dict] = []
        self.logger = logger

    async def initialize(self):
        """初始化技能追踪器"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if self.storage_path.exists():
            await self.load()
        else:
            # 初始化一些基础技能
            self._init_default_skills()
            await self.save()

    def _init_default_skills(self):
        """初始化默认技能"""
        default_skills = [
            "Python", "async/await", "type hints", "dataclass", "decorator",
            "context manager", "generator", "FastAPI", "Django", "Flask",
            "pytest", "asyncio", "concurrency", "design patterns"
        ]

        for skill_name in default_skills:
            self.skills[skill_name.lower()] = Skill(
                name=skill_name,
                category="python"
            )

    async def load(self):
        """加载技能数据"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 加载技能
            for skill_data in data.get("skills", []):
                skill = Skill(**skill_data)
                self.skills[skill.name.lower()] = skill

            # 加载历史
            self.history = data.get("history", [])

            self.logger.info(f"加载了 {len(self.skills)} 个技能")

        except Exception as e:
            self.logger.error(f"加载技能数据失败: {e}")
            self._init_default_skills()

    async def save(self):
        """保存技能数据"""
        try:
            data = {
                "skills": [skill.to_dict() for skill in self.skills.values()],
                "history": self.history,
                "updated_at": datetime.now().isoformat()
            }

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存技能数据失败: {e}")

    def update_from_learnings(self, learnings: List[Dict[str, Any]]):
        """从学习内容更新技能"""
        today = datetime.now().isoformat()

        for learning in learnings:
            # 提取标签作为技能
            tags = learning.get("tags", [])
            title = learning.get("title", "")

            # 从标签更新
            for tag in tags:
                self._update_skill(tag, today)

            # 从标题提取技能
            for word in title.split():
                if len(word) > 3 and word.isalpha():
                    self._update_skill(word, today)

        # 记录历史
        self.history.append({
            "date": today,
            "learnings_count": len(learnings),
            "skills_count": len(self.skills)
        })

    def update_from_content(self, content: str, title: str, tags: List[str]):
        """从内容更新技能"""
        today = datetime.now().isoformat()

        # 从标签更新
        for tag in tags:
            self._update_skill(tag, today)

        # 从标题提取
        for word in title.split():
            if len(word) > 3 and word.isalpha():
                self._update_skill(word, today)

        # 从内容中提取常见技术术语
        tech_terms = [
            "async", "await", "decorator", "generator", "coroutine",
            "dataclass", "type hint", "context manager", "protocol",
            "FastAPI", "Django", "Flask", "pytest", "unittest",
            "asyncio", "threading", "multiprocessing", "concurrency"
        ]

        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                self._update_skill(term, today)

    def _update_skill(self, name: str, date: str):
        """更新单个技能"""
        key = name.lower()

        if key not in self.skills:
            self.skills[key] = Skill(name=name)

        self.skills[key].mentions += 1
        self.skills[key].last_practiced = date

    def get_skill_map(self) -> Dict[str, Any]:
        """获取技能地图"""
        # 按类别分组
        categories = {}

        for skill in self.skills.values():
            cat = skill.category or "general"
            if cat not in categories:
                categories[cat] = []

            categories[cat].append({
                "name": skill.name,
                "mentions": skill.mentions,
                "last_practiced": skill.last_practiced
            })

        # 每个类别内按热度排序
        for cat in categories:
            categories[cat].sort(key=lambda x: x["mentions"], reverse=True)

        return {
            "categories": categories,
            "total_skills": len(self.skills),
            "total_mentions": sum(s.mentions for s in self.skills.values())
        }

    def get_tag_cloud(self, limit: int = 50) -> List[tuple]:
        """获取标签云（按热度排序）"""
        sorted_skills = sorted(
            self.skills.items(),
            key=lambda x: x[1].mentions,
            reverse=True
        )

        return [(name, skill.mentions) for name, skill in sorted_skills[:limit]]

    def get_top_skills(self, limit: int = 10) -> List[Skill]:
        """获取热门技能"""
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: s.mentions,
            reverse=True
        )

        return sorted_skills[:limit]

    def get_skill_details(self, skill_name: str) -> Dict[str, Any]:
        """获取技能详情"""
        key = skill_name.lower()
        skill = self.skills.get(key)

        if not skill:
            return None

        return skill.to_dict()
