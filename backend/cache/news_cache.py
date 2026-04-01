from typing import List, Dict, Any, Optional

from backend.config import cache_conf
CATEGORIES_kEY = "news:categories"
NEWS_LIST_PERFIX = 'news:list:'
NEWS_COUNT_PREFIX = "news:count:"
NEWS_DETAIL_PREFIX = "news:detail:"
NEWS_RECOMMEND_PREFIX = "news:recommend:"
#读类别缓存
async def get_categories_cache():
    return await cache_conf.get_json_cache(CATEGORIES_kEY)
#设置类别缓存
async def set_categories_cache(data: List[Dict[str, Any]], expire: int= 7200):
    return await cache_conf.set_cache(CATEGORIES_kEY, data, expire)


#读新闻列表缓存
async def get_news_list_cache(category_id: Optional[int], page: int, page_size:int):
    category_id = category_id if category_id is not None else "all"
    key=f"{NEWS_LIST_PERFIX}{category_id}:{page}:{page_size}"
    return await cache_conf.get_json_cache(key)
# 设置新闻列表缓存
async def set_news_list_cache(category_id: Optional[int], page: int, page_size:int, data: List[Dict[str, Any]], expire: int= 1800):
    category_id = category_id if category_id is not None else "all"
    key=f"{NEWS_LIST_PERFIX}{category_id}:{page}:{page_size}"
    return await cache_conf.set_cache(key, data, expire)


async def delete_news_list_cache(category_id: Optional[int]):
    category_id = category_id if category_id is not None else "all"
    pattern = f"{NEWS_LIST_PERFIX}{category_id}:*"
    return await cache_conf.delete_cache_pattern(pattern)


async def delete_news_count_cache(category_id: Optional[int]):
    category_id = category_id if category_id is not None else "all"
    key = f"{NEWS_COUNT_PREFIX}{category_id}"
    return await cache_conf.delete_cache(key)


async def get_news_count_cache(category_id: Optional[int]):
    category_id = category_id if category_id is not None else "all"
    key = f"{NEWS_COUNT_PREFIX}{category_id}"
    return await cache_conf.get_json_cache(key)


async def set_news_count_cache(category_id: Optional[int], count: int, expire: int = 1800):
    category_id = category_id if category_id is not None else "all"
    key = f"{NEWS_COUNT_PREFIX}{category_id}"
    return await cache_conf.set_cache(key, count, expire)


async def get_news_detail_cache(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await cache_conf.get_json_cache(key)


async def set_news_detail_cache(news_id: int, data: Dict[str, Any], expire: int = 3600):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await cache_conf.set_cache(key, data, expire)


async def delete_news_detail_cache(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await cache_conf.delete_cache(key)


async def get_news_recommend_cache(category_id: int, news_id: int, limit: int):
    key = f"{NEWS_RECOMMEND_PREFIX}{category_id}:{news_id}:{limit}"
    return await cache_conf.get_json_cache(key)


async def set_news_recommend_cache(category_id: int, news_id: int, limit: int, data: List[Dict[str, Any]], expire: int = 1800):
    key = f"{NEWS_RECOMMEND_PREFIX}{category_id}:{news_id}:{limit}"
    return await cache_conf.set_cache(key, data, expire)


async def delete_news_recommend_cache_by_category(category_id: int):
    pattern = f"{NEWS_RECOMMEND_PREFIX}{category_id}:*"
    return await cache_conf.delete_cache_pattern(pattern)
