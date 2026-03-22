import { defineStore } from 'pinia'

export const useAuthStore = defineStore('admin-auth', {
  state: () => ({
    accessToken: '',
    refreshToken: '',
    userInfo: null,
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.accessToken),
    isAdmin: (state) => state.userInfo?.role === 'admin',
    username: (state) => state.userInfo?.username || '',
    nickname: (state) => state.userInfo?.nickname || state.userInfo?.username || '管理员',
  },

  actions: {
    setSession(payload = {}) {
      this.accessToken = payload.accessToken || payload.token || ''
      this.refreshToken = payload.refreshToken || ''
      this.userInfo = payload.userInfo || null
    },

    updateAccessToken(token) {
      this.accessToken = token || ''
    },

    setUserInfo(userInfo) {
      this.userInfo = userInfo || null
    },

    clearSession() {
      this.accessToken = ''
      this.refreshToken = ''
      this.userInfo = null
    },
  },

  persist: true,
})
