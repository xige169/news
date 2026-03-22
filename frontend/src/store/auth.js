import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    refreshToken: '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    username: (state) => state.userInfo?.username || ''
  },

  actions: {
    setAuth(authPayload) {
      this.token = authPayload?.accessToken || authPayload?.token || ''
      this.refreshToken = authPayload?.refreshToken || ''
      this.userInfo = authPayload?.userInfo || null
    },

    setUserInfo(userInfo) {
      this.userInfo = userInfo
    },

    clearAuth() {
      this.token = ''
      this.refreshToken = ''
      this.userInfo = null
    }
  },

  persist: true
})
