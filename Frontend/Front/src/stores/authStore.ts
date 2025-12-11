// src/stores/authStore.ts
import { defineStore } from 'pinia'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

export interface AuthState {
  access: string | null
  refresh: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    access: null,
    refresh: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
  },

  actions: {
    async login(email: string, password: string) {
      // ✅ CSRF 처리
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')

      // ✅ SimpleJWT 로그인 (email 로그인 기준)
      const res = await client.post(
        '/api/token/', // 👉 baseURL 그대로 쓴다고 했으니까 여기 유지
        { email, password }, // ← 백엔드가 username 기반이면 key만 username으로 바꾸면 됨
        {
          headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        },
      )

      const { access, refresh } = res.data as {
        access: string
        refresh: string
      }

      // ✅ 상태에 저장 (persist가 알아서 localStorage(nestudy-auth)에 저장)
      this.access = access
      this.refresh = refresh
    },

    logout() {
      this.access = null
      this.refresh = null
      // nestudy-auth까지 같이 지우고 싶으면 아래 주석 해제
      localStorage.removeItem('nestudy-auth')
    },
  },

  // 🔐 Pinia persist 플러그인 사용
  persist: {
    key: 'nestudy-auth',
    storage: localStorage,
    paths: ['access', 'refresh'],
  },
})
