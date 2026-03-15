from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.db_conf import get_db_session
from backend.models.users import User
from backend.schemas.history import (
    HistoryAddRequest,
    HistoryAddResponse,
    HistoryItemResponse,
    HistoryListResponse,
)
from backend.utils import auth
from backend.crud import history
from backend.utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(
    news_data: HistoryAddRequest,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    添加历史记录
    """
    add_news_history = await history.add_news_history(news_data.news_id, user.id, db)
    if not add_news_history:
        raise HTTPException(status_code=400, detail="添加失败")

    return success_response(
        message="添加成功",
        data=HistoryAddResponse.model_validate(add_news_history)
    )

@router.get("/list")
async def get_history_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, le=100, alias="pageSize"),
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取历史记录列表
    """
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    news_list = [
        HistoryItemResponse.model_validate({
            **news.__dict__,
            "view_time": view_time
        })
        for news, view_time in rows
    ]

    return success_response(
        message="获取成功",
        data=HistoryListResponse(
            list=news_list,
            total=total,
            has_more=total > page * page_size
        )
    )

@router.delete("/delete/{history_id}")
async def delete_one_history(
    history_id: int,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    删除一条历史记录
    """
    delete_result = await history.delete_one_history(history_id, user.id, db)
    if not delete_result:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return success_response(message="删除成功")

@router.delete("/clear")
async def clear_history(
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    清空历史记录
    """
    await history.clear_history(user.id, db)
    return success_response(message="清空成功")
