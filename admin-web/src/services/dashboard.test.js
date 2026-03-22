import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchDashboardSummary } from './dashboard.js'

test('fetchDashboardSummary hits the admin dashboard summary endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input) => {
      calls.push(input)
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            code: 200,
            message: 'success',
            data: {
              newsTotal: 10,
            },
          }
        },
      }
    },
  })

  await fetchDashboardSummary(api)

  assert.equal(calls[0], '/api/admin/dashboard/summary')
})
