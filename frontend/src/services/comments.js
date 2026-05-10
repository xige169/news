import { apiClient } from './http.js'

export const fetchComments = async ({ newsId, page = 1, pageSize = 20 }, request = apiClient) => {
  return request(
    `/api/comment/list?newsId=${newsId}&page=${page}&pageSize=${pageSize}`,
    { auth: false }
  )
}

export const postComment = async ({ newsId, content, parentId = null }, request = apiClient) => {
  const body = parentId == null
    ? { newsId, content }
    : { newsId, content, parentId }
  return request('/api/comment/add', {
    method: 'POST',
    body: JSON.stringify(body)
  })
}

export const deleteComment = async (commentId, request = apiClient) => {
  return request(`/api/comment/${commentId}`, {
    method: 'DELETE'
  })
}

export const likeComment = async ({ commentId, like }, request = apiClient) => {
  return request(`/api/comment/${commentId}/like`, {
    method: 'POST',
    body: JSON.stringify({ like })
  })
}
