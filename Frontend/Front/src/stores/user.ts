import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.js'
import router from '@/router'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const TTL_MS = 5 * 60 * 1000 // 5분 캐시 유지

export const useUserStore = defineStore('user', () => {
  // ✅ 상태
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

  // ✅ 프로필 불러오기 (너의 코드 반영)
  async function _fetchUser() {
    loading.value = true
    error.value = ''
    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')
      const { data } = await axios.get(`${API_BASE}/accounts/search/`, {
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken },
      })

      profile.value.email = data.email || ''
      profile.value.nickname = data.username || ''
      if (data.profile_img && !data.profile_img.startsWith('http')) {
        profile.value.avatar_url = `${API_BASE}${data.profile_img}`
      } else {
        profile.value.avatar_url = data.profile_img || ''
      }

      lastFetched.value = Date.now()
    } catch (e: any) {
      console.error(e)
      profile.value.email = ''
      profile.value.nickname = ''
      profile.value.avatar_url = ''
      if (e?.response?.status === 401) {
        // 세션 만료 → 로그인 페이지로 이동
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

  // ✅ 로그아웃
  async function logout() {
    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')
      await axios.post(`${API_BASE}/accounts/logout/`, null, {
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken },
      })
    } catch (e) {
      console.error(e)
    } finally {
      reset()
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
