import { apiClient } from './http.js'

export const fetchDashboardSummary = async (request = apiClient) => {
  return request('/api/admin/dashboard/summary')
}
