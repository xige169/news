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
