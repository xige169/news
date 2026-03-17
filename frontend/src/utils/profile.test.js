import test from 'node:test'
import assert from 'node:assert/strict'

import { normalizeGender, toGenderLabel } from './profile.js'

test('normalizeGender keeps backend enum values and falls back to unknown', () => {
  assert.equal(normalizeGender('male'), 'male')
  assert.equal(normalizeGender('female'), 'female')
  assert.equal(normalizeGender('unknown'), 'unknown')
  assert.equal(normalizeGender('未知'), 'unknown')
  assert.equal(normalizeGender(''), 'unknown')
})

test('toGenderLabel converts backend enum to chinese labels', () => {
  assert.equal(toGenderLabel('male'), '男')
  assert.equal(toGenderLabel('female'), '女')
  assert.equal(toGenderLabel('unknown'), '未设置')
  assert.equal(toGenderLabel('bad-value'), '未设置')
})
