import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchCurrentUser, login, logoutSession, refreshSession, register } from './auth.js'

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

test('refreshSession posts refresh token to refresh endpoint', async () => {
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
              token: 'next-access',
              accessToken: 'next-access',
              refreshToken: 'next-refresh'
            }
          }
        }
      }
    }
  })

  const payload = await refreshSession({ refreshToken: 'refresh-1' }, api)

  assert.equal(calls[0].input, '/api/user/refresh')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(calls[0].init.body, JSON.stringify({ refreshToken: 'refresh-1' }))
  assert.equal(payload.refreshToken, 'next-refresh')
})

test('logoutSession posts to logout endpoint with bearer token', async () => {
  const calls = []
  const api = createApiClient({
    getToken: () => 'access-1',
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

  await logoutSession(api)

  assert.equal(calls[0].input, '/api/user/logout')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(calls[0].init.headers.Authorization, 'Bearer access-1')
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

test('api client refreshes token and retries once after 401', async () => {
  const calls = []
  let currentToken = 'expired-access'
  let refreshCalls = 0
  const api = createApiClient({
    getToken: () => currentToken,
    refreshAccessToken: async () => {
      refreshCalls += 1
      currentToken = 'fresh-access'
      return currentToken
    },
    fetchImpl: async (input, init) => {
      calls.push({ input, init })
      if (calls.length === 1) {
        return {
          ok: false,
          status: 401,
          async json() {
            return {
              detail: '无效令牌或者令牌已过期'
            }
          }
        }
      }

      return {
        ok: true,
        status: 200,
        async json() {
          return {
            code: 200,
            message: 'success',
            data: {
              id: 8,
              username: 'retry-user'
            }
          }
        }
      }
    }
  })

  const user = await fetchCurrentUser(api)

  assert.equal(refreshCalls, 1)
  assert.equal(calls.length, 2)
  assert.equal(calls[0].init.headers.Authorization, 'Bearer expired-access')
  assert.equal(calls[1].init.headers.Authorization, 'Bearer fresh-access')
  assert.equal(user.username, 'retry-user')
})
