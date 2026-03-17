import { apiClient } from './http.js'

export const addHistoryEntry = async (newsId, request = apiClient) => {
  return request('/api/history/add', {
    method: 'POST',
    body: JSON.stringify({ newsId })
  })
}

export const fetchHistoryList = async ({ page = 1, pageSize = 10 }, request = apiClient) => {
  return request(`/api/history/list?page=${page}&pageSize=${pageSize}`)
}

export const removeHistoryEntry = async (historyId, request = apiClient) => {
  return request(`/api/history/delete/${historyId}`, {
    method: 'DELETE'
  })
}

export const clearHistoryEntries = async (request = apiClient) => {
  return request('/api/history/clear', {
    method: 'DELETE'
  })
}
