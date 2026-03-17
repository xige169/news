import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchCurrentUser, login, register } from './auth.js'

test('login posts credentials to the login endpoint', async () => {
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
              token: 'token-1',
              userInfo: {
                id: 1,
                username: 'alice'
              }
            }
          }
        }
      }
    }
  })

  const payload = await login({ username: 'alice', password: 'secret' }, api)

  assert.equal(calls[0].input, '/api/user/login')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(calls[0].init.body, JSON.stringify({ username: 'alice', password: 'secret' }))
  assert.equal(payload.token, 'token-1')
})

test('register posts credentials to the register endpoint', async () => {
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
              token: 'token-2',
              userInfo: {
                id: 2,
                username: 'bob'
              }
            }
          }
        }
      }
    }
  })

  const payload = await register({ username: 'bob', password: 'secret' }, api)

  assert.equal(calls[0].input, '/api/user/register')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(payload.userInfo.username, 'bob')
})

test('fetchCurrentUser sends bearer token for authenticated requests', async () => {
  const calls = []
  const api = createApiClient({
    getToken: () => 'abc123',
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
              id: 7,
              username: 'carol'
            }
          }
        }
      }
    }
  })

  const user = await fetchCurrentUser(api)

  assert.equal(calls[0].input, '/api/user/info')
  assert.equal(calls[0].init.headers.Authorization, 'Bearer abc123')
  assert.equal(user.username, 'carol')
})

test('api client calls onUnauthorized when backend returns 401', async () => {
  let unauthorizedCalls = 0
  const api = createApiClient({
    getToken: () => 'expired-token',
    onUnauthorized: () => {
      unauthorizedCalls += 1
    },
    fetchImpl: async () => ({
      ok: false,
      status: 401,
      async json() {
        return {
          detail: '无效令牌或者令牌已过期'
        }
      }
    })
  })

  await assert.rejects(() => fetchCurrentUser(api), /无效令牌或者令牌已过期/)
  assert.equal(unauthorizedCalls, 1)
})
