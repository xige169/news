import test from 'node:test'
import assert from 'node:assert/strict'

import { addHistoryEntry, fetchHistoryList, removeHistoryEntry } from './history.js'
import {
  addFavorite,
  checkFavorite,
  clearFavorites,
  fetchFavoriteList,
  removeFavorite
} from './favorite.js'
import { fetchNewsDetail } from './news.js'
import { createApiClient } from './http.js'

test('fetchNewsDetail requests the backend detail endpoint by id', async () => {
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
            data: { id: 9, title: 'detail' }
          }
        }
      }
    }
  })

  const detail = await fetchNewsDetail(9, api)

  assert.equal(calls[0], '/api/news/detail?id=9')
  assert.equal(detail.id, 9)
})

test('favorite services follow backend contract for check add remove and list', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            code: 200,
            message: 'success',
            data: { list: [], total: 0, hasMore: false, isFavorite: true }
          }
        }
      }
    }
  })

  await checkFavorite(3, api)
  await addFavorite(3, api)
  await removeFavorite(3, api)
  await fetchFavoriteList({ page: 2, pageSize: 5 }, api)
  await clearFavorites(api)

  assert.equal(calls[0].input, '/api/favorite/check?newsId=3')
  assert.equal(calls[1].input, '/api/favorite/add')
  assert.equal(calls[1].init.body, JSON.stringify({ newsId: 3 }))
  assert.equal(calls[2].input, '/api/favorite/remove?newsId=3')
  assert.equal(calls[2].init.method, 'DELETE')
  assert.equal(calls[3].input, '/api/favorite/list?page=2&pageSize=5')
  assert.equal(calls[4].input, '/api/favorite/clear')
})

test('history services follow backend contract for add list and delete', async () => {
  const calls = []
  const api = createApiClient({
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            code: 200,
            message: 'success',
            data: { list: [], total: 0, hasMore: false }
          }
        }
      }
    }
  })

  await addHistoryEntry(8, api)
  await fetchHistoryList({ page: 3, pageSize: 6 }, api)
  await removeHistoryEntry(12, api)

  assert.equal(calls[0].input, '/api/history/add')
  assert.equal(calls[0].init.body, JSON.stringify({ newsId: 8 }))
  assert.equal(calls[1].input, '/api/history/list?page=3&pageSize=6')
  assert.equal(calls[2].input, '/api/history/delete/12')
  assert.equal(calls[2].init.method, 'DELETE')
})
