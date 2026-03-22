import { apiClient } from './http.js'

const appendQuery = (params = {}) => {
  const searchParams = new URLSearchParams()

  if (params.page) searchParams.set('page', String(params.page))
  if (params.pageSize) searchParams.set('pageSize', String(params.pageSize))
  if (params.keyword) searchParams.set('keyword', String(params.keyword))
  if (params.status) searchParams.set('status', String(params.status))
  if (params.categoryId) searchParams.set('categoryId', String(params.categoryId))

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

export const fetchNewsList = async (params = {}, request = apiClient) => {
  return request(`/api/admin/news${appendQuery(params)}`)
}

export const fetchNewsDetail = async (newsId, request = apiClient) => {
  return request(`/api/admin/news/${newsId}`)
}

export const createNews = async (payload, request = apiClient) => {
  return request('/api/admin/news', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export const updateNews = async (newsId, payload, request = apiClient) => {
  return request(`/api/admin/news/${newsId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export const updateNewsStatus = async (newsId, status, request = apiClient) => {
  return request(`/api/admin/news/${newsId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })
}

export const deleteNews = async (newsId, request = apiClient) => {
  return request(`/api/admin/news/${newsId}`, {
    method: 'DELETE',
  })
}
