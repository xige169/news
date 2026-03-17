import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchCurrentUser, updatePassword, updateProfile } from './auth.js'

test('updateProfile sends the backend profile payload', async () => {
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
            data: {
              id: 1,
              username: 'alice',
              nickname: 'Alice'
            }
          }
        }
      }
    }
  })

  const user = await updateProfile({
    nickname: 'Alice',
    avatar: 'https://example.com/avatar.png',
    gender: '女',
    bio: '编辑记者',
    phone: '13800000000'
  }, api)

  assert.equal(calls[0].input, '/api/user/update')
  assert.equal(calls[0].init.method, 'PUT')
  assert.equal(user.nickname, 'Alice')
})

test('updatePassword uses the backend field aliases', async () => {
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
            data: null
          }
        }
      }
    }
  })

  await updatePassword({
    oldPassword: 'old-secret',
    newPassword: 'new-secret'
  }, api)

  assert.equal(calls[0].input, '/api/user/password')
  assert.equal(calls[0].init.body, JSON.stringify({
    oldPassword: 'old-secret',
    newPassword: 'new-secret'
  }))
})

test('fetchCurrentUser keeps using the profile endpoint', async () => {
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
            data: {
              id: 5,
              username: 'editor'
            }
          }
        }
      }
    }
  })

  const user = await fetchCurrentUser(api)

  assert.equal(calls[0], '/api/user/info')
  assert.equal(user.username, 'editor')
})
