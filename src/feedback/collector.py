"""用户反馈系统"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from loguru import logger


@dataclass
class Feedback:
    """用户反馈"""
    id: str
    timestamp: str
    learning_id: str  # 哪条知识
    rating: int  # 1-5 星
    useful: bool  # 是否有用
    problem: Optional[str]  # 有什么问题
    user_comment: Optional[str]  # 用户评论


class FeedbackCollector:
    """反馈收集器"""

    def __init__(self, feedback_dir: Path = None):
        self.feedback_dir = feedback_dir or Path("./data/feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedbacks.json"

    def save_feedback(self, feedback: Feedback) -> None:
        """保存反馈"""
        feedbacks = self._load_feedbacks()
        feedbacks.append(asdict(feedback))

        with open(self.feedback_file, "w") as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)

        logger.info(f"反馈已保存: {feedback.learning_id} - {feedback.rating}⭐")

    def _load_feedbacks(self) -> List[Dict]:
        """加载所有反馈"""
        if self.feedback_file.exists():
            with open(self.feedback_file, "r") as f:
                return json.load(f)
        return []

    def get_feedback_stats(self, days: int = 7) -> Dict:
        """获取反馈统计"""
        feedbacks = self._load_feedbacks()

        # 过滤最近N天的反馈
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            f for f in feedbacks
            if datetime.fromisoformat(f["timestamp"]) > cutoff
        ]

        if not recent:
            return {"total": 0, "avg_rating": 0, "useful_rate": 0}

        total = len(recent)
        avg_rating = sum(f["rating"] for f in recent) / total
        useful_rate = sum(1 for f in recent if f["useful"]) / total

        # 统计主要问题
        problem_counts = {}
        for f in recent:
            if f.get("problem"):
                problem_counts[f["problem"]] = problem_counts.get(f["problem"], 0) + 1

        return {
            "total": total,
            "avg_rating": avg_rating,
            "useful_rate": useful_rate,
            "main_problems": sorted(problem_counts.items(), key=lambda x: -x[1])
        }

    def get_learning_feedback(self, learning_id: str) -> List[Dict]:
        """获取某条知识的所有反馈"""
        feedbacks = self._load_feedbacks()
        return [f for f in feedbacks if f["learning_id"] == learning_id]
