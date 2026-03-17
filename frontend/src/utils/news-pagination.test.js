import test from 'node:test'
import assert from 'node:assert/strict'

import { mergeNewsPage, resetPaginationState } from './news-pagination.js'

test('resetPaginationState initializes first page loading state', () => {
  assert.deepEqual(resetPaginationState(), {
    items: [],
    page: 1,
    hasMore: true
  })
})

test('mergeNewsPage replaces list on first page and appends on next page', () => {
  const firstPage = mergeNewsPage(resetPaginationState(), [{ id: 1 }, { id: 2 }], false, 1)
  const nextPage = mergeNewsPage(firstPage, [{ id: 3 }, { id: 4 }], true, 2)

  assert.deepEqual(firstPage, {
    items: [{ id: 1 }, { id: 2 }],
    page: 1,
    hasMore: false
  })
  assert.deepEqual(nextPage, {
    items: [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }],
    page: 2,
    hasMore: true
  })
})
