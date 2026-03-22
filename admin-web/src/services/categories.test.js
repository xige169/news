import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { createCategory, deleteCategory, fetchCategories, updateCategory } from './categories.js'

test('fetchCategories hits the admin categories endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input) => {
      calls.push(input)
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: [] }
        },
      }
    },
  })

  await fetchCategories(api)

  assert.equal(calls[0], '/api/admin/categories')
})

test('createCategory posts payload to the admin categories endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 2 } }
        },
      }
    },
  })

  await createCategory({ name: '科技', sortOrder: 1 }, api)

  assert.equal(calls[0].input, '/api/admin/categories')
  assert.equal(calls[0].init.method, 'POST')
})

test('updateCategory uses the admin category update endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 2 } }
        },
      }
    },
  })

  await updateCategory(2, { name: '财经' }, api)

  assert.equal(calls[0].input, '/api/admin/categories/2')
  assert.equal(calls[0].init.method, 'PUT')
})

test('deleteCategory uses the admin category delete endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: null }
        },
      }
    },
  })

  await deleteCategory(2, api)

  assert.equal(calls[0].input, '/api/admin/categories/2')
  assert.equal(calls[0].init.method, 'DELETE')
})
