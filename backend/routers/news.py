from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import news
from backend.config.db_conf import get_db_session
from backend.crud.news import get_news_recommend

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession= Depends(get_db_session)):
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
    category_id:int =Query(..., alias="categoryId"),
    page: int = Query(default=1),
    pagesize: int = Query(default=10,le=100,alias="pageSize"),
    db: AsyncSession= Depends(get_db_session)
):
    offset = (page - 1) * pagesize
    news_list = await news.get_news_list(db,category_id, offset, pagesize)
    total = await news.get_news_count(db,category_id)
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }

@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    db: AsyncSession= Depends(get_db_session)
):
    news_detail = await news.get_news_detail(db,news_id)
    if news_detail is None:
        raise HTTPException(status_code=404, detail="新闻不存在")

    news_view = await news.update_news_views(db,news_detail.id)
    if news_view is None:
        raise HTTPException(status_code=404, detail="更新新闻浏览量失败")

    news_recommend = await get_news_recommend(db,news_detail.id,news_detail.category_id)
    return {
      "code": 200,
      "message": "success",
      "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": news_recommend
      }
    }

