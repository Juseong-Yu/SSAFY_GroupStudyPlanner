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
  name: string
  leader?: string
  role?: 'leader' | 'member' | string
  is_active?: boolean
  joined_at?: string
  created_at?: string
}

export const useStudiesStore = defineStore('studies', () => {
  // state
  const leader = ref<Study[]>([])
  const member = ref<Study[]>([])
  const loading = ref(false)
  const error = ref('')
  const lastFetched = ref<number | null>(null)
  let inFlight: Promise<void> | null = null

  // derived
  const leaderCount = computed(() => leader.value.length)
  const memberCount = computed(() => member.value.length)

  // freshness
  const isFresh = () => lastFetched.value && Date.now() - lastFetched.value < TTL_MS

  // ---- parser ----
  function parseAndSet(payload: any) {
    // 디버그용(원하면 주석처리)
    // console.log('[studies] raw payload:', payload)

    let arr: any[] = []

    if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
      // 케이스 C: { studies: [...] }  ✅ 지금 네 응답
      if (Array.isArray(payload.studies)) {
        arr = payload.studies
      }
      // 케이스 A: { leader: [], member: [] } (이전 호환)
      else if (Array.isArray(payload.leader) || Array.isArray(payload.member)) {
        const L = (payload.leader || []).map((s: any) => ({ ...s, role: 'leader' }))
        const M = (payload.member || []).map((s: any) => ({ ...s, role: s.role ?? 'member' }))
        arr = [...L, ...M]
      }
    } else if (Array.isArray(payload)) {
      // 케이스 B: [ ... ] (flat 배열)
      arr = payload
    }

    const all: Study[] = (arr || []).map((s: any) => ({
      id: s.id,
      name: s.name ?? s.title ?? '제목 없음',
      leader: s.leader ?? '',
      role: s.role ?? '',
      // 파이썬 True/False는 실제 JSON에선 true/false로 직렬화됨 (DRF/JsonResponse)
      is_active: s.is_active ?? true,
      joined_at: s.joined_at ?? '',
      created_at: s.created_at ?? '',
    }))

    leader.value = all.filter((s) => s.role === 'leader')
    member.value = all.filter((s) => s.role !== 'leader')
  }

  // ---- fetcher ----
  async function _fetchStudies() {
    loading.value = true
    error.value = ''
    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')
      const { data } = await axios.get(`${API_BASE}/studies/study_list/`, {
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken },
      })
      // console.log('[studies] GET /get_my_study data:', datastudy_liststudy_list)
      parseAndSet(data)
      lastFetched.value = Date.now()
    } catch (e: any) {
      console.error(e)
      leader.value = []
      member.value = []
      if (e?.response?.status === 401) {
        router.push('/login')
      } else {
        error.value = '스터디 목록을 불러오지 못했습니다.'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  // public actions
  async function loadIfNeeded(opts?: { force?: boolean }) {
    const force = !!opts?.force
    if (!force && isFresh() && (leader.value.length || member.value.length)) return
    if (inFlight) return inFlight
    inFlight = _fetchStudies().finally(() => (inFlight = null))
    return inFlight
  }

  async function refresh() {
    return loadIfNeeded({ force: true })
  }

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
