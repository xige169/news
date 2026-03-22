import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import {
  createNews,
  deleteNews,
  fetchNewsDetail,
  fetchNewsList,
  updateNews,
  updateNewsStatus,
} from './news.js'

test('fetchNewsList sends pagination and filters to the admin news endpoint', async () => {
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
            data: { list: [], total: 0 },
          }
        },
      }
    },
  })

  await fetchNewsList({ page: 2, pageSize: 15, keyword: 'AI', status: 'published', categoryId: 3 }, api)

  assert.equal(calls[0], '/api/admin/news?page=2&pageSize=15&keyword=AI&status=published&categoryId=3')
})

test('fetchNewsDetail hits the admin news detail endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input) => {
      calls.push(input)
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 8 } }
        },
      }
    },
  })

  await fetchNewsDetail(8, api)

  assert.equal(calls[0], '/api/admin/news/8')
})

test('createNews posts draft payload to the admin news endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 1 } }
        },
      }
    },
  })

  await createNews({ title: '新稿件' }, api)

  assert.equal(calls[0].input, '/api/admin/news')
  assert.equal(calls[0].init.method, 'POST')
})

test('updateNews uses the admin news update endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 8 } }
        },
      }
    },
  })

  await updateNews(8, { title: '改标题' }, api)

  assert.equal(calls[0].input, '/api/admin/news/8')
  assert.equal(calls[0].init.method, 'PUT')
})

test('updateNewsStatus uses the dedicated status endpoint', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return { code: 200, message: 'success', data: { id: 8, status: 'offline' } }
        },
      }
    },
  })

  await updateNewsStatus(8, 'offline', api)

  assert.equal(calls[0].input, '/api/admin/news/8/status')
  assert.equal(calls[0].init.method, 'PUT')
  assert.equal(calls[0].init.body, JSON.stringify({ status: 'offline' }))
})

test('deleteNews uses the admin news delete endpoint', async () => {
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

  await deleteNews(8, api)

  assert.equal(calls[0].input, '/api/admin/news/8')
  assert.equal(calls[0].init.method, 'DELETE')
})
