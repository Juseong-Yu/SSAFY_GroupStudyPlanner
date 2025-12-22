// src/stores/authStore.ts
import { defineStore } from 'pinia'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import type { Dictionary } from '@fullcalendar/core/internal'

export interface AuthState {
  access: string | null
  refresh: string | null
  discord: Dictionary | null
}

type DiscordLoginCallbackResponse = {
  type: 'login' | 'register' | null
  access: string
  refresh: string
  user: {
    id: number
    email: string
    username: string | null
  }
  discord: {
    discord_id: string
    username: string
    email: string
  }
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    access: null,
    refresh: null,
    discord: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
  },

  actions: {
    async login(email: string, password: string) {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')

      const res = await client.post(
        '/api/token/',
        { email, password },
        {
          headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        },
      )

      const { access, refresh } = res.data as { access: string; refresh: string }

      this.access = access
      this.refresh = refresh
    },

    /**
     * ✅ Discord OAuth 로그인 (프론트에서 code 받아 호출)
     * 사용처: DiscordLoginCallbackView.vue 같은 곳에서
     * await auth.oauthLoginWithDiscord(code)
     */
    async oauthLoginWithDiscord(code: string) {
      if (!code) throw new Error('OAuth code is required')

      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')

      const res = await client.get<DiscordLoginCallbackResponse>(
        `/api/auth/discord/login/callback/?code=${code}`,
        {
          headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        },
      )

      const { access, refresh, type } = res.data
      // ✅ persist가 localStorage(nestudy-auth)에 저장
      if (type === 'login') {
        this.access = access
        this.refresh = refresh
        // (선택) user도 저장하고 싶으면 AuthState에 user 추가해서 여기서 넣으면 됨
        return res.data
      } else if (type === 'register') {
        this.discord = res.data.discord
        return res.data
      }
    },

    logout() {
      this.access = null
      this.refresh = null
      localStorage.removeItem('nestudy-auth')
    },
  },

  persist: {
    key: 'nestudy-auth',
    storage: localStorage,
    paths: ['access', 'refresh'],
  },
})
