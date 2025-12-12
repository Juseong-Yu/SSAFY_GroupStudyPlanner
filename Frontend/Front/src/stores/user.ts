// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import router from '@/router'
import{ isAxiosError } from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TTL_MS = 5 * 60 * 1000 // 5분 캐시 유지

export const useUserStore = defineStore('user', () => {
  // ✅ 상태 d
  const profile = ref({
    email: '',
    nickname: '',
    avatar_url: '',
  })
  const loading = ref(false)
  const error = ref('')
  const lastFetched = ref<number | null>(null)
  let inFlight: Promise<void> | null = null
  
  // ✅ 신선도 확인
  const isFresh = () => lastFetched.value && Date.now() - lastFetched.value < TTL_MS

  // ✅ 프로필 불러오기
  async function _fetchUser() {
    loading.value = true
    error.value = ''
    try {
      // 여기서는 CSRF/Authorization 전부 client 인터셉터가 처리함
      const { data } = await client.get('/api/search/')

      profile.value.email = data.email || ''
      profile.value.nickname = data.username || ''

      if (data.profile_img && !data.profile_img.startsWith('http')) {
        profile.value.avatar_url = `${API_BASE}${data.profile_img}`
      } else {
        profile.value.avatar_url = data.profile_img || ''
      }

      lastFetched.value = Date.now()
    } catch (e: any) {
      console.error('[useUserStore] _fetchUser error:', e)
      profile.value.email = ''
      profile.value.nickname = ''
      profile.value.avatar_url = ''

      if (e?.response?.status === 401) {
        // 토큰 만료 / 인증 실패 → 로그인 페이지로
        router.push('/login')
      } else {
        error.value = '사용자 정보를 불러오지 못했습니다.'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  // ✅ 필요할 때만 요청 (중복 방지 + TTL 적용)
  async function loadIfNeeded(opts?: { force?: boolean }) {
    const force = !!opts?.force
    if (!force && profile.value.nickname && isFresh()) return
    if (inFlight) return inFlight
    inFlight = _fetchUser().finally(() => (inFlight = null))
    return inFlight
  }

  // ✅ 로그아웃 (원하면 여기서도 client.post('/api/logout/') 쓸 수 있음)
  async function logout() {
  // 1️⃣ localStorage에서 nestudy-auth 읽어서 refresh 꺼내기
  let refresh: string | null = null
  const raw = localStorage.getItem('nestudy-auth')

  if (raw) {
    try {
      const parsed = JSON.parse(raw) as {
        access?: string
        refresh?: string
        [key: string]: unknown
      }
      refresh = parsed.refresh ?? null
    } catch (e) {
      console.error('[logout] nestudy-auth JSON parse error:', e)
    }
  }

  try {
    // 2️⃣ refresh 있으면 백엔드에 넘겨서 블랙리스트에 등록
    if (refresh) {
      await client.post('/api/logout/', { refresh })
    } else {
      console.warn('[logout] refresh 토큰이 없어서 서버 로그아웃은 스킵')
    }
  } catch (e) {
    if (isAxiosError(e)) {
      console.error('[logout] status:', e.response?.status)
      console.error('[logout] data:', e.response?.data)
    } else {
      console.error('[logout] unknown error:', e)
    }
  } finally {
    // 3️⃣ 프론트 상태/스토리지 정리
    reset()

    // nestudy-auth 기반이면 이거 하나만 써도 되지만,
    // 혹시 예전에 따로 저장해둔 키가 있으면 같이 정리
    localStorage.removeItem('nestudy-auth')
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')

    router.push('/login')
  }
}

  // ✅ 상태 초기화
  function reset() {
    profile.value.email = ''
    profile.value.nickname = ''
    profile.value.avatar_url = ''
    error.value = ''
    lastFetched.value = null
  }

  return {
    profile,
    loading,
    error,
    loadIfNeeded,
    logout,
    reset,
  }
})
