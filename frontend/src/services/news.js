import { apiClient } from './http.js'

export const fetchCategories = async (request = apiClient) => {
  return request('/api/news/categories', {
    auth: false
  })
}

export const fetchNewsList = async ({ categoryId, page = 1, pageSize = 10 }, request = apiClient) => {
  const params = new URLSearchParams({
    categoryId: String(categoryId),
    page: String(page),
    pageSize: String(pageSize)
  })

  return request(`/api/news/list?${params.toString()}`, {
    auth: false
  })
}

export const fetchNewsDetail = async (id, request = apiClient) => {
  return request(`/api/news/detail?id=${id}`, {
    auth: false
  })
}

export const searchNews = async ({ keyword, categoryId, page = 1, pageSize = 10 }, request = apiClient) => {
  const params = new URLSearchParams()
  params.set('q', String(keyword))

  if (categoryId) {
    params.set('categoryId', String(categoryId))
  }
  params.set('page', String(page))
  params.set('pageSize', String(pageSize))

  return request(`/api/news/search?${params.toString()}`, {
    auth: false
  })
}

export const fetchHotNews = async ({ page = 1, pageSize = 10 }, request = apiClient) => {
  return request(`/api/news/hot?page=${page}&pageSize=${pageSize}`, {
    auth: false
  })
}

export const fetchRecommendedNews = async ({ page = 1, pageSize = 10 }, request = apiClient) => {
  return request(`/api/news/recommend?page=${page}&pageSize=${pageSize}`)
}
