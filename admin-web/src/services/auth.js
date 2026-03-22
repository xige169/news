import { apiClient } from './http.js'

export const loginAdmin = async (payload, request = apiClient) => {
  return request('/api/user/login', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload),
  })
}

export const refreshAdminToken = async (refreshToken, request = apiClient) => {
  return request('/api/user/refresh', {
    method: 'POST',
    auth: false,
    body: JSON.stringify({ refreshToken }),
  })
}

export const fetchAdminProfile = async (request = apiClient) => {
  return request('/api/user/info')
}

export const logoutAdmin = async (request = apiClient) => {
  return request('/api/user/logout', {
    method: 'POST',
  })
}
