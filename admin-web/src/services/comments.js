import { apiClient } from './http.js'

const appendQuery = (params = {}) => {
  const searchParams = new URLSearchParams()

  if (params.page) searchParams.set('page', String(params.page))
  if (params.pageSize) searchParams.set('pageSize', String(params.pageSize))
  if (params.keyword) searchParams.set('keyword', String(params.keyword))
  if (params.newsId) searchParams.set('newsId', String(params.newsId))

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

export const fetchComments = async (params = {}, request = apiClient) => {
  return request(`/api/admin/comments${appendQuery(params)}`)
}

export const deleteComment = async (commentId, request = apiClient) => {
  return request(`/api/admin/comments/${commentId}`, {
    method: 'DELETE',
  })
}
