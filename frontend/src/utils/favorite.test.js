import test from 'node:test'
import assert from 'node:assert/strict'

import { getFavoriteActionMeta } from './favorite.js'

test('getFavoriteActionMeta returns idle and active star states', () => {
  assert.deepEqual(getFavoriteActionMeta(false, false), {
    icon: 'star-o',
    label: '收藏',
    pressed: false
  })

  assert.deepEqual(getFavoriteActionMeta(true, false), {
    icon: 'star',
    label: '已收藏',
    pressed: true
  })
})

test('getFavoriteActionMeta returns loading label while request is running', () => {
  assert.deepEqual(getFavoriteActionMeta(false, true), {
    icon: 'star-o',
    label: '处理中',
    pressed: false
  })
})
