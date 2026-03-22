export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const runtimeConfig = {
  getToken: () => '',
  refreshAccessToken: async () => '',
  onUnauthorized: () => {},
}

const buildHeaders = (headers, token) => {
  const nextHeaders = {
    Accept: 'application/json',
    ...headers,
  }

  if (token) {
    nextHeaders.Authorization = `Bearer ${token}`
  }

  if (!nextHeaders['Content-Type'] && nextHeaders['content-type'] !== null) {
    nextHeaders['Content-Type'] = 'application/json'
  }

  return nextHeaders
}

export const createApiClient = ({
  fetchImpl = (...args) => globalThis.fetch(...args),
  getToken = () => runtimeConfig.getToken(),
  refreshAccessToken = (...args) => runtimeConfig.refreshAccessToken(...args),
  onUnauthorized = () => runtimeConfig.onUnauthorized(),
} = {}) => {
  return async (url, options = {}) => {
    const token = options.auth === false ? '' : getToken()
    const headers = buildHeaders(options.headers, token)

    if (options.headers?.['content-type'] === null) {
      delete headers['content-type']
    }

    if (options.headers?.['Content-Type'] === null) {
      delete headers['Content-Type']
    }

    const response = await fetchImpl(url, {
      ...options,
      headers,
    })

    if (response.status === 401 && options.auth !== false && !options._retried) {
      try {
        const nextToken = await refreshAccessToken()
        if (nextToken) {
          return createApiClient({
            fetchImpl,
            getToken: () => nextToken,
            refreshAccessToken,
            onUnauthorized,
          })(url, {
            ...options,
            _retried: true,
          })
        }
      } catch {
        onUnauthorized()
      }
    }

    let payload = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }

    if (response.status === 401) {
      onUnauthorized()
    }

    if (!response.ok) {
      throw new ApiError(payload?.detail || payload?.message || `请求失败: ${response.status}`, response.status)
    }

    if (payload?.code !== 200) {
      throw new ApiError(payload?.message || '接口返回异常', response.status)
    }

    return payload.data
  }
}

export const configureApiClient = (config = {}) => {
  if (typeof config.getToken === 'function') {
    runtimeConfig.getToken = config.getToken
  }
  if (typeof config.refreshAccessToken === 'function') {
    runtimeConfig.refreshAccessToken = config.refreshAccessToken
  }
  if (typeof config.onUnauthorized === 'function') {
    runtimeConfig.onUnauthorized = config.onUnauthorized
  }
}

export const apiClient = createApiClient()
