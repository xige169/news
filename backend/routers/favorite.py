from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from backend.config.db_conf import get_db_session
from backend.crud import favorite as favorite_crud
from backend.models.users import User
from backend.utils import auth
from backend.utils.response import success_response
from backend.schemas.favorite import FavoriteAddResponse, FavoriteCheckResponse, FavoriteNewsItemResponse

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(news_id:int =Query(...,alias="newsId"), user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db_session)):
    is_favorite = await favorite_crud.is_news_favorite(news_id, user.id, db)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorite))

@router.post("/add")
async def add_favorite(news_data: FavoriteAddResponse, user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db_session)):
    result = await favorite_crud.add_news_favorite(news_data.news_id, user.id, db)
    return success_response(message="收藏成功", data=result)

@router.delete("/remove")
async def remove_favorite(news_id:int =Query(...,alias="newsId"), user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db_session)):
    result = await favorite_crud.remove_news_favorite(news_id, user.id, db)
    if not result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="取消收藏成功")

@router.get("/list")
async def get_favorite_list(page: int = Query(default=1), page_size:int = Query(default=10,le=100,alias="pageSize"), user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db_session)):
    rows, total = await favorite_crud.get_favorite_list(db, page, page_size, user.id)
    favorite_list = [
        FavoriteNewsItemResponse.model_validate({
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id
        }).model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
            exclude={"summary", "tags", "hot_score"}
        )
        for news, favorite_time, favorite_id in rows
    ]
    has_more = total > page * page_size
    data = {
        "list": favorite_list,
        "total": total,
        "hasMore": has_more
    }
    return success_response(message="获取收藏列表成功", data=data)

@router.delete("/clear")
async def clear_favorite_list(user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db_session)):
    count = await favorite_crud.clear_favorite_list(db, user.id)
    if not count:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户收藏列表为空")
    return success_response(message=f"清空了{count}条记录")
