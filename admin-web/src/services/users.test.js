import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchUsers, updateUserRole } from './users.js'

test('fetchUsers sends pagination and filters to the admin users endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input) => {
      calls.push(input)
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { list: [], total: 0 } }
        },
      }
    },
  })

  await fetchUsers({ page: 3, pageSize: 12, keyword: 'editor', role: 'admin' }, api)

  assert.equal(calls[0], '/api/admin/users?page=3&pageSize=12&keyword=editor&role=admin')
})

test('updateUserRole uses the user role update endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 3, role: 'admin' } }
        },
      }
    },
  })

  await updateUserRole(3, 'admin', api)

  assert.equal(calls[0].input, '/api/admin/users/3/role')
  assert.equal(calls[0].init.method, 'PUT')
  assert.equal(calls[0].init.body, JSON.stringify({ role: 'admin' }))
})
