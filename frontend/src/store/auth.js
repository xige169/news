import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    username: (state) => state.userInfo?.username || ''
  },

  actions: {
    setAuth(authPayload) {
      this.token = authPayload?.token || ''
      this.userInfo = authPayload?.userInfo || null
    },

    setUserInfo(userInfo) {
      this.userInfo = userInfo
    },

    clearAuth() {
      this.token = ''
      this.userInfo = null
    }
  },

  persist: true
})
