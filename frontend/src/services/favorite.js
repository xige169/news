import { apiClient } from './http.js'

export const checkFavorite = async (newsId, request = apiClient) => {
  return request(`/api/favorite/check?newsId=${newsId}`)
}

export const addFavorite = async (newsId, request = apiClient) => {
  return request('/api/favorite/add', {
    method: 'POST',
    body: JSON.stringify({ newsId })
  })
}

export const removeFavorite = async (newsId, request = apiClient) => {
  return request(`/api/favorite/remove?newsId=${newsId}`, {
    method: 'DELETE'
  })
}

export const fetchFavoriteList = async ({ page = 1, pageSize = 10 }, request = apiClient) => {
  return request(`/api/favorite/list?page=${page}&pageSize=${pageSize}`)
}

export const clearFavorites = async (request = apiClient) => {
  return request('/api/favorite/clear', {
    method: 'DELETE'
  })
}
