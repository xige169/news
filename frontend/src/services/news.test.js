import test from 'node:test'
import assert from 'node:assert/strict'

import { fetchCategories, fetchHotNews, fetchNewsList, fetchRecommendedNews, searchNews } from './news.js'

test('fetchCategories uses the proxied api path and returns category data', async () => {
  const calls = []
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (input) => {
    calls.push(input)
    return {
      ok: true,
      async json() {
        return {
          code: 200,
          message: 'success',
          data: [{ id: 1, name: '科技' }]
        }
      }
    }
  }

  try {
    const categories = await fetchCategories()

    assert.deepEqual(calls, ['/api/news/categories'])
    assert.deepEqual(categories, [{ id: 1, name: '科技' }])
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('fetchNewsList uses query params required by backend and returns list payload', async () => {
  const calls = []
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (input) => {
    calls.push(input)
    return {
      ok: true,
      async json() {
        return {
          code: 200,
          message: 'success',
          data: {
            list: [
              {
                id: 11,
                title: '测试新闻',
                description: '摘要',
                author: '新闻社',
                categoryId: 3,
                views: 99,
                publishTime: '2026-03-17T08:00:00'
              }
            ],
            total: 1,
            hasMore: false
          }
        }
      }
    }
  }

  try {
    const payload = await fetchNewsList({ categoryId: 3, page: 2, pageSize: 5 })

    assert.deepEqual(calls, ['/api/news/list?categoryId=3&page=2&pageSize=5'])
    assert.equal(payload.list[0].id, 11)
    assert.equal(payload.hasMore, false)
    assert.equal(payload.total, 1)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('searchNews uses keyword and optional category params required by backend', async () => {
  const calls = []
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (input) => {
    calls.push(input)
    return {
      ok: true,
      async json() {
        return {
          code: 200,
          message: 'success',
          data: {
            list: [{ id: 15, title: 'AI 搜索结果' }],
            total: 1,
            hasMore: false
          }
        }
      }
    }
  }

  try {
    const payload = await searchNews({ keyword: 'AI', categoryId: 2, page: 1, pageSize: 8 })

    assert.deepEqual(calls, ['/api/news/search?q=AI&categoryId=2&page=1&pageSize=8'])
    assert.equal(payload.list[0].title, 'AI 搜索结果')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('fetchHotNews uses the hot endpoint and returns payload', async () => {
  const calls = []
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (input) => {
    calls.push(input)
    return {
      ok: true,
      async json() {
        return {
          code: 200,
          message: 'success',
          data: {
            list: [{ id: 2, title: '热门头条' }],
            total: 1,
            hasMore: false
          }
        }
      }
    }
  }

  try {
    const payload = await fetchHotNews({ page: 1, pageSize: 6 })

    assert.deepEqual(calls, ['/api/news/hot?page=1&pageSize=6'])
    assert.equal(payload.list[0].title, '热门头条')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('fetchRecommendedNews uses the recommend endpoint and returns source', async () => {
  const calls = []
  const originalFetch = globalThis.fetch

  globalThis.fetch = async (input) => {
    calls.push(input)
    return {
      ok: true,
      async json() {
        return {
          code: 200,
          message: 'success',
          data: {
            list: [{ id: 18, title: '为你推荐' }],
            total: 1,
            hasMore: false,
            source: 'personalized'
          }
        }
      }
    }
  }

  try {
    const payload = await fetchRecommendedNews({ page: 2, pageSize: 6 })

    assert.deepEqual(calls, ['/api/news/recommend?page=2&pageSize=6'])
    assert.equal(payload.source, 'personalized')
    assert.equal(payload.list[0].id, 18)
  } finally {
    globalThis.fetch = originalFetch
  }
})
