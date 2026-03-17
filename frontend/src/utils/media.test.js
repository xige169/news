import test from 'node:test'
import assert from 'node:assert/strict'

import { getAvatarUrl, getNewsImageUrl } from './media.js'

test('getNewsImageUrl returns backend image and falls back when missing', () => {
  assert.equal(getNewsImageUrl('https://example.com/news.jpg'), 'https://example.com/news.jpg')
  assert.equal(getNewsImageUrl(''), 'https://picsum.photos/seed/news-cover/960/540')
  assert.equal(getNewsImageUrl(null), 'https://picsum.photos/seed/news-cover/960/540')
})

test('getAvatarUrl returns backend avatar and falls back when missing', () => {
  assert.equal(getAvatarUrl('https://example.com/avatar.png'), 'https://example.com/avatar.png')
  assert.equal(getAvatarUrl(''), 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg')
  assert.equal(getAvatarUrl(undefined), 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg')
})
