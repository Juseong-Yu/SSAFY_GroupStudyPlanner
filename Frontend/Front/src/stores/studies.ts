// src/stores/studies.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import client from '@/api/client'
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

// 백엔드에서 오는 raw 형태 (느슨하게 정의)
interface RawStudy {
  id: number | string
  name?: string
  title?: string
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
  const isFresh = () => lastFetched.value !== null && Date.now() - lastFetched.value < TTL_MS

  // ---- parser ----
function parseAndSet(payload: unknown) {
  let arr: RawStudy[] = []

  if (Array.isArray(payload)) {
    // 케이스 B: [ ... ] (flat 배열)
    arr = payload as RawStudy[]
  } else if (payload && typeof payload === 'object') {
    const obj = payload as {
      studies?: RawStudy[]
      leader?: RawStudy[]
      member?: RawStudy[]
    }

    // 케이스 C: { studies: [...] }
    if (Array.isArray(obj.studies)) {
      arr = obj.studies
    }
    // 케이스 A: { leader: [], member: [] }
    else if (Array.isArray(obj.leader) || Array.isArray(obj.member)) {
      const L = (obj.leader ?? []).map((s) => ({
        ...s,
        role: 'leader' as const, // 여기만 leader로 강제
      }))
      const M = (obj.member ?? []).map((s) => ({
        ...s, // role은 있는 그대로 두기 (기본값은 아래에서 처리)
      }))
      arr = [...L, ...M]
    }
  }

  const all: Study[] = (arr ?? []).map((s) => ({
    id: s.id,
    name: s.name ?? s.title ?? '제목 없음',
    leader: s.leader ?? '',
    role: s.role ?? '',          // 👉 여기서 기본값 처리
    is_active: s.is_active ?? true,
    joined_at: s.joined_at ?? '',
    created_at: s.created_at ?? '',
  }))

  leader.value = all.filter((s) => s.role === 'leader')
  member.value = all.filter((s) => s.role !== 'leader')
}


  // ---- fetcher ----
  async function _fetchStudies(): Promise<void> {
    loading.value = true
    error.value = ''
    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')

      const { data } = await client.get(`${API_BASE}/api/study_list/`, {
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken ?? '' },
      })

      // console.log('[studies] GET /studies/study_list data:', data)
      parseAndSet(data)
      lastFetched.value = Date.now()
    } catch (e: unknown) {
      console.error(e)
      leader.value = []
      member.value = []

      if (axios.isAxiosError(e)) {
        if (e.response?.status === 401) {
          // 세션 만료 → 로그인 페이지로 이동
          router.push('/login')
        } else {
          error.value = '스터디 목록을 불러오지 못했습니다.'
        }
      } else {
        error.value = '알 수 없는 오류가 발생했습니다.'
      }

      throw e
    } finally {
      loading.value = false
    }
  }

  // public actions
  async function loadIfNeeded(opts?: { force?: boolean }): Promise<void> {
    const force = !!opts?.force
    if (!force && isFresh() && (leader.value.length || member.value.length)) return
    if (inFlight) return inFlight
    inFlight = _fetchStudies().finally(() => {
      inFlight = null
    })
    return inFlight
  }

  async function refresh(): Promise<void> {
    return loadIfNeeded({ force: true })
  }

  function reset(): void {
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
    lastFetched,
    // derived
    leaderCount,
    memberCount,
    // actions
    loadIfNeeded,
    refresh,
    reset,
  }
})
