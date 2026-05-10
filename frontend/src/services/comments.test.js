import test from 'node:test'
import assert from 'node:assert/strict'

import { fetchComments, postComment, deleteComment, likeComment } from './comments.js'

const stubFetch = (responseData) => {
  const calls = []
  globalThis.fetch = async (input, init) => {
    calls.push({ input, init })
    return {
      ok: true,
      status: 200,
      async json() {
        return { code: 200, message: 'ok', data: responseData }
      }
    }
  }
  return calls
}

test('fetchComments hits list endpoint with paging params and no auth', async () => {
  const originalFetch = globalThis.fetch
  const calls = stubFetch({ list: [], total: 0, hasMore: false })
  try {
    const data = await fetchComments({ newsId: 5, page: 2, pageSize: 10 })
    assert.equal(calls[0].input, '/api/comment/list?newsId=5&page=2&pageSize=10')
    assert.equal(calls[0].init?.headers?.Authorization, undefined)
    assert.deepEqual(data, { list: [], total: 0, hasMore: false })
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('postComment posts JSON body with newsId, content and optional parentId', async () => {
  const originalFetch = globalThis.fetch
  const calls = stubFetch({ id: 1 })
  try {
    await postComment({ newsId: 3, content: 'hi', parentId: 7 })
    assert.equal(calls[0].input, '/api/comment/add')
    assert.equal(calls[0].init.method, 'POST')
    assert.deepEqual(JSON.parse(calls[0].init.body), { newsId: 3, content: 'hi', parentId: 7 })
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('postComment omits parentId when null', async () => {
  const originalFetch = globalThis.fetch
  const calls = stubFetch({ id: 1 })
  try {
    await postComment({ newsId: 3, content: 'hi' })
    assert.deepEqual(JSON.parse(calls[0].init.body), { newsId: 3, content: 'hi' })
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('deleteComment uses DELETE on /api/comment/{id}', async () => {
  const originalFetch = globalThis.fetch
  const calls = stubFetch(null)
  try {
    await deleteComment(11)
    assert.equal(calls[0].input, '/api/comment/11')
    assert.equal(calls[0].init.method, 'DELETE')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('likeComment posts like flag to /like endpoint', async () => {
  const originalFetch = globalThis.fetch
  const calls = stubFetch({ commentId: 11, likeCount: 1, liked: true })
  try {
    const data = await likeComment({ commentId: 11, like: true })
    assert.equal(calls[0].input, '/api/comment/11/like')
    assert.equal(calls[0].init.method, 'POST')
    assert.deepEqual(JSON.parse(calls[0].init.body), { like: true })
    assert.equal(data.liked, true)
    assert.equal(data.likeCount, 1)
  } finally {
    globalThis.fetch = originalFetch
  }
})
