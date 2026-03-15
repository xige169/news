from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


class HistoryAddResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    news_id: int = Field(..., alias="newsId")
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class HistoryItemResponse(NewsItemBase):
    publish_time: datetime | None = Field(None, alias="publishTime")
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
