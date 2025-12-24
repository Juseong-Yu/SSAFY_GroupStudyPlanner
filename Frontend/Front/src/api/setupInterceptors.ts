// src/api/setupInterceptors.ts
import type {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios'
import axios from 'axios'
import router from '@/router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

interface StoredTokens {
  access: string | null
  refresh: string | null
}

function getStoredTokens(): StoredTokens {
  const raw = localStorage.getItem('nestudy-auth')
  if (!raw) return { access: null, refresh: null }

  try {
    const parsed = JSON.parse(raw) as Partial<StoredTokens>
    return {
      access: parsed.access ?? null,
      refresh: parsed.refresh ?? null,
    }
  } catch (e) {
    console.error('[auth] failed to parse nestudy-auth from localStorage', e)
    return { access: null, refresh: null }
  }
}

function setTokens(partial: Partial<StoredTokens>) {
  const raw = localStorage.getItem('nestudy-auth')
  let stored: any = {}
  try {
    stored = raw ? JSON.parse(raw) : {}
  } catch {
    stored = {}
  }

  if (partial.access !== undefined) stored.access = partial.access
  if (partial.refresh !== undefined) stored.refresh = partial.refresh

  localStorage.setItem('nestudy-auth', JSON.stringify(stored))
}

/**
 * ✅ 이 요청들은 "401/400"이 정상적으로 날 수 있는 구간이라
 * 인터셉터에서 refresh/redirect/logout를 절대 걸면 안 됨
 */
const AUTH_EXCLUDE_PATHS = [
  '/api/token/', // 로그인
  '/api/token/refresh/', // refresh (자기 자신)
  '/api/login_with_discord/', // 디스코드 로그인 시작
  '/api/auth/discord/login/callback/', // 디스코드 로그인 콜백(백엔드 호출)
]

function isExcluded(url?: string) {
  if (!url) return false
  return AUTH_EXCLUDE_PATHS.some((p) => url.includes(p))
}

// ✅ refresh 동시성 제어
let isRefreshing = false
let refreshQueue: Array<(token: string | null) => void> = []

function resolveQueue(token: string | null) {
  refreshQueue.forEach((cb) => cb(token))
  refreshQueue = []
}

export function setupInterceptors(client: AxiosInstance) {
  /**
   * ✅ Request: access 토큰 자동 첨부
   */
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const { access } = getStoredTokens()

      if (access) {
        config.headers = config.headers ?? {}
        config.headers.Authorization = `Bearer ${access}`
      }

      return config
    },
    (error) => Promise.reject(error),
  )

  /**
   * ✅ Response: 401이면 refresh 시도 (exclude는 제외)
   */
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }

      const status = error.response?.status
      const url = originalRequest?.url

      // ✅ 0) 로그인/refresh/OAuth 시작 구간은 절대 개입하지 않기
      if (isExcluded(url)) {
        return Promise.reject(error)
      }

      // ✅ 1) 네트워크 에러는 여기서 강제 리다이렉트하지 말고 그대로 throw
      // (S3 배포 환경에서 네트워크 불안정/잘못된 baseURL 때문에 reload 루프 생길 수 있음)
      if (!status) {
        return Promise.reject(error)
      }

      // ✅ 2) 401 처리: refresh 시도
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        const { refresh } = getStoredTokens()

        // refresh 없으면 그냥 로그아웃 + 로그인 화면 (리로드 금지)
        if (!refresh) {
          localStorage.removeItem('nestudy-auth')
          await router.replace({ name: 'login' })
          return Promise.reject(error)
        }

        // 이미 refresh 중이면 큐에 대기
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            refreshQueue.push((token) => {
              if (!token) return reject(error)
              originalRequest.headers = originalRequest.headers ?? {}
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(client(originalRequest))
            })
          })
        }

        try {
          isRefreshing = true

          await ensureCsrf()
          const csrftoken = getCookie('csrftoken')

          const res = await axios.post(
            `${client.defaults.baseURL}/api/token/refresh/`,
            { refresh },
            {
              headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
              withCredentials: true,
            },
          )

          const data = res.data as { access: string; refresh?: string }
          const newAccess = data.access
          const newRefresh = data.refresh

          // 토큰 저장
          setTokens({
            access: newAccess,
            refresh: newRefresh ?? refresh,
          })

          // 대기 중인 요청들 풀기
          resolveQueue(newAccess)

          // 원 요청 재시도
          originalRequest.headers = originalRequest.headers ?? {}
          originalRequest.headers.Authorization = `Bearer ${newAccess}`

          return client(originalRequest)
        } catch (refreshError) {
          console.error('❌ refresh 실패 → 로그아웃 필요', refreshError)

          // 큐에 대기 중인 요청도 실패 처리
          resolveQueue(null)

          localStorage.removeItem('nestudy-auth')
          await router.replace({ name: 'login' })

          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    },
  )
}
