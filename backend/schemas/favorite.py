from pydantic import BaseModel, Field, ConfigDict

from backend.schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

class FavoriteAddResponse(BaseModel):
    news_id: str = Field(..., alias="newsId")

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: str = Field(..., alias="favoriteId")
    favorite_time: str = Field(..., alias="favoriteTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total: int
    has_More: bool = Field(..., alias="hasMore")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
