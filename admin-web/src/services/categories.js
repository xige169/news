import { apiClient } from './http.js'

export const fetchCategories = async (request = apiClient) => {
  return request('/api/admin/categories')
}

export const createCategory = async (payload, request = apiClient) => {
  return request('/api/admin/categories', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export const updateCategory = async (categoryId, payload, request = apiClient) => {
  return request(`/api/admin/categories/${categoryId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export const deleteCategory = async (categoryId, request = apiClient) => {
  return request(`/api/admin/categories/${categoryId}`, {
    method: 'DELETE',
  })
}
