import { apiClient } from './http.js'

const appendQuery = (params = {}) => {
  const searchParams = new URLSearchParams()

  if (params.page) searchParams.set('page', String(params.page))
  if (params.pageSize) searchParams.set('pageSize', String(params.pageSize))
  if (params.keyword) searchParams.set('keyword', String(params.keyword))
  if (params.role) searchParams.set('role', String(params.role))

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

export const fetchUsers = async (params = {}, request = apiClient) => {
  return request(`/api/admin/users${appendQuery(params)}`)
}

export const updateUserRole = async (userId, role, request = apiClient) => {
  return request(`/api/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  })
}
