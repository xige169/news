import { apiClient } from './http.js'

export const login = async (payload, request = apiClient) => {
  return request('/api/user/login', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload)
  })
}

export const register = async (payload, request = apiClient) => {
  return request('/api/user/register', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload)
  })
}

export const fetchCurrentUser = async (request = apiClient) => {
  return request('/api/user/info')
}

export const refreshSession = async (payload, request = apiClient) => {
  return request('/api/user/refresh', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload)
  })
}

export const logoutSession = async (request = apiClient) => {
  return request('/api/user/logout', {
    method: 'POST'
  })
}

export const updateProfile = async (payload, request = apiClient) => {
  return request('/api/user/update', {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
}

export const updatePassword = async (payload, request = apiClient) => {
  return request('/api/user/password', {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
}
