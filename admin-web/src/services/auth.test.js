import test from 'node:test'
import assert from 'node:assert/strict'

import { createApiClient } from './http.js'
import { fetchAdminProfile, loginAdmin, refreshAdminToken } from './auth.js'

test('loginAdmin posts credentials without auth header', async () => {
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
              accessToken: 'access-token',
            },
          }
        },
      }
    },
  })

  await loginAdmin({ username: 'admin', password: 'secret' }, api)

  assert.equal(calls[0].input, '/api/user/login')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(calls[0].init.headers.Authorization, undefined)
})

test('refreshAdminToken posts refresh token without auth header', async () => {
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
              accessToken: 'next-access',
              refreshToken: 'next-refresh',
            },
          }
        },
      }
    },
  })

  await refreshAdminToken('refresh-token', api)

  assert.equal(calls[0].input, '/api/user/refresh')
  assert.equal(calls[0].init.method, 'POST')
  assert.equal(calls[0].init.body, JSON.stringify({ refreshToken: 'refresh-token' }))
  assert.equal(calls[0].init.headers.Authorization, undefined)
})

test('fetchAdminProfile requests current user info', async () => {
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
              id: 1,
              role: 'admin',
            },
          }
        },
      }
    },
  })

  await fetchAdminProfile(api)

  assert.equal(calls[0], '/api/user/info')
})
