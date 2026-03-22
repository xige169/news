from datetime import datetime
import re
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NewsItemBase(BaseModel):
    id: int
    title: str
    description:Optional[str]= None
    summary: Optional[str] = None
    image:Optional[str]= None
    author:Optional[str]= None
    tags: list[str] = Field(default_factory=list)
    category_id: int = Field(alias="categoryId")
    views: int
    hot_score: float | None = Field(None, alias="hotScore")
    publish_time: Optional[datetime]= Field(None, alias="publishTime")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


def build_summary(description: Optional[str], content: Optional[str], max_length: int = 88) -> str:
    source = (description or content or "").strip()
    if not source:
        return "暂无摘要"
    normalized = re.sub(r"\s+", " ", source)
    return normalized if len(normalized) <= max_length else f"{normalized[:max_length].rstrip()}..."


def build_tags(*parts: Optional[str], limit: int = 3) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()

    for part in parts:
        if not part:
            continue
        for token in re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", part):
            normalized = token.strip()
            if not normalized or normalized in seen:
                continue
            tags.append(normalized[:12])
            seen.add(normalized)
            if len(tags) >= limit:
                return tags

    return tags
