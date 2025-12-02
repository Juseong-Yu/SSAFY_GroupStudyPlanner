// src/stores/studyRoleStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE_URL as string
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

export type StudyRole = 'leader' | 'member' | 'guest'

export interface StudyRoleInfo {
  studyId: number
  role: StudyRole
  leaderId: number
  userId: number
  username: string
  email: string
}

interface FetchResult {
  ok: boolean
  status?: number
  error?: string
}

export const useStudyRoleStore = defineStore('studyRole', () => {
  // key: studyId(string), value: StudyRoleInfo
  const rolesByStudyId = ref<Record<string, StudyRoleInfo>>({})

  // 현재 활성 스터디 (선택사항: 필요 없으면 안 써도 됨)
  const currentStudyId = ref<string | null>(null)

  function getRoleInfo(studyId: string | number): StudyRoleInfo | null {
    const key = String(studyId)
    return rolesByStudyId.value[key] ?? null
  }

  function isLeader(studyId: string | number): boolean {
    const info = getRoleInfo(studyId)
    return info?.role === 'leader'
  }

  function getRole(studyId: string | number): StudyRole | null {
    const info = getRoleInfo(studyId)
    return info?.role ?? null
  }

  function resetStudyRole(studyId: string | number) {
    const key = String(studyId)
    const copy = { ...rolesByStudyId.value }
    delete copy[key]
    rolesByStudyId.value = copy
    if (currentStudyId.value === key) {
      currentStudyId.value = null
    }
  }

  function resetAll() {
    rolesByStudyId.value = {}
    currentStudyId.value = null
  }

  /**
   * 스터디 내 내 역할 조회 API 호출
   * - 성공 시 rolesByStudyId에 저장
   * - 결과는 FetchResult 형태로 반환 (라우터 가드에서 상태 코드 보고 분기)
   */
  async function fetchMyRole(studyId: string | number): Promise<FetchResult> {
    const key = String(studyId)

    try {
      await ensureCsrf()
      const csrftoken = getCookie('csrftoken')

      const res = await axios.get(
        `${API_BASE}/studies/${key}/get_my_role/`,
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': csrftoken,
          },
        },
      )

      const data = res.data as {
        user: { id: number; username: string; email: string }
        study: { id: number; name: string; created_at: string; leader: number }
        role: 'leader' | 'member' | string
      }

      const info: StudyRoleInfo = {
        studyId: data.study.id,
        role: (data.role as StudyRole) ?? 'guest',
        leaderId: data.study.leader,
        userId: data.user.id,
        username: data.user.username,
        email: data.user.email,
      }

      rolesByStudyId.value[key] = info
      currentStudyId.value = key

      return { ok: true }
    } catch (err: any) {
      console.error('fetchMyRole error', err)
      const status = err?.response?.status
      let msg = '역할 조회 중 오류가 발생했습니다.'

      if (status === 403) msg = '이 스터디에 접근할 권한이 없습니다.'
      if (status === 404) msg = '존재하지 않는 스터디입니다.'

      // 해당 스터디 정보는 지워둠 (혹시 이전 캐시가 있었다면 초기화)
      resetStudyRole(studyId)

      return {
        ok: false,
        status,
        error: msg,
      }
    }
  }

  const currentRoleInfo = computed(() => {
    if (!currentStudyId.value) return null
    return rolesByStudyId.value[currentStudyId.value] ?? null
  })

  const currentRole = computed<StudyRole | null>(() => {
    return currentRoleInfo.value?.role ?? null
  })

  const currentIsLeader = computed<boolean>(() => {
    return currentRole.value === 'leader'
  })

  return {
    rolesByStudyId,
    currentStudyId,
    currentRoleInfo,
    currentRole,
    currentIsLeader,

    getRoleInfo,
    getRole,
    isLeader,
    resetStudyRole,
    resetAll,
    fetchMyRole,
  }
})
