from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from backend.schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class FavoriteAddResponse(BaseModel):
    news_id: int = Field(..., alias="newsId")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
