// src/stores/studies.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import router from '@/router'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const TTL_MS = 5 * 60 * 1000 // 5분 캐시

export interface Study {
  id: number | string
  title: string
  role?: 'leader' | 'member' | string
}

export const useStudiesStore = defineStore('studies', () => {
  // ✅ 상태
  const leader = ref<Study[]>([])
  const member = ref<Study[]>([])
  const loading = ref(false)
  const error = ref('')
  const lastFetched = ref<number | null>(null)
  let inFlight: Promise<void> | null = null

  // ✅ 파생값
  const leaderCount = computed(() => leader.value.length)
  const memberCount = computed(() => member.value.length)

  // ✅ 신선도
  const isFresh = () => lastFetched.value && Date.now() - lastFetched.value < TTL_MS

  // ✅ 응답 파서 (두 가지 형태 지원)
  function parseAndSet(payload: any) {
    let _leader: Study[] = []
    let _member: Study[] = []

    if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
      // 형태 A: { leader:[], member:[] }
      _leader = Array.isArray(payload.leader) ? payload.leader : []
      _member = Array.isArray(payload.member) ? payload.member : []
    } else if (Array.isArray(payload)) {
      // 형태 B: [{ id, title|name, role }]
      const arr = payload as Study[]
      _leader = arr.filter((s) => s.role === 'leader')
      _member = arr.filter((s) => s.role !== 'leader')
    }

    // title/name 폴백 정리
    leader.value = (_leader || []).map((s: any) => ({
      id: s.id,
      title: s.title ?? s.name ?? '제목 없음',
      role: 'leader',
    }))
    member.value = (_member || []).map((s: any) => ({
      id: s.id,
      title: s.title ?? s.name ?? '제목 없음',
      role: 'member',
    }))
  }

  // ✅ 실제 호출
  async function _fetchStudies() {
    loading.value = true
    error.value = ''
    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')
      const { data } = await axios.get(`${API_BASE}/studies/get_my_study/`, {
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken },
      })
      parseAndSet(data)
      lastFetched.value = Date.now()
    } catch (e: any) {
      console.error(e)
      leader.value = []
      member.value = []
      if (e?.response?.status === 401) {
        // 세션 만료 → 로그인으로
        router.push('/login')
      } else {
        error.value = '스터디 목록을 불러오지 못했습니다.'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  // ✅ 필요할 때만 요청 (TTL + 중복 호출 방지)
  async function loadIfNeeded(opts?: { force?: boolean }) {
    const force = !!opts?.force
    if (!force && isFresh() && (leader.value.length || member.value.length)) return
    if (inFlight) return inFlight
    inFlight = _fetchStudies().finally(() => (inFlight = null))
    return inFlight
  }

  // ✅ 강제 새로고침(생성/참여 직후에 사용)
  async function refresh() {
    return loadIfNeeded({ force: true })
  }

  // ✅ 리셋
  function reset() {
    leader.value = []
    member.value = []
    loading.value = false
    error.value = ''
    lastFetched.value = null
  }

  return {
    // state
    leader,
    member,
    loading,
    error,
    // derived
    leaderCount,
    memberCount,
    // actions
    loadIfNeeded,
    refresh,
    reset,
  }
})
