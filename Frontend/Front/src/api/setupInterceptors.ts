// src/api/setupInterceptors.ts
import type {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

// 🔹 authStore persist (key: 'nestudy-auth')에서 access/refresh 꺼내는 헬퍼
interface StoredTokens {
  access: string | null
  refresh: string | null
}

function getStoredTokens(): StoredTokens {
  const raw = localStorage.getItem('nestudy-auth')
  if (!raw) {
    return { access: null, refresh: null }
  }

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

function setAccessToken(access: string | null) {
  const raw = localStorage.getItem('nestudy-auth')
  let stored: any = {}
  try {
    stored = raw ? JSON.parse(raw) : {}
  } catch {
    stored = {}
  }
  stored.access = access
  localStorage.setItem('nestudy-auth', JSON.stringify(stored))
}

export function setupInterceptors(client: AxiosInstance) {
  /** =====================================================================================
   *  🔹 1) Request Interceptor: 모든 요청에 Authorization + CSRF 자동 추가
   * ===================================================================================== */
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // CSRF: 필요할 때 자동 보냄
      const csrftoken = getCookie('csrftoken')
      if (csrftoken) {
        config.headers = config.headers ?? {}
        config.headers['X-CSRFToken'] = csrftoken
      }

      // JWT Authorization 헤더 자동 추가 (nestudy-auth 기준)
      const { access } = getStoredTokens()
      // 디버깅용
      console.log('[setupInterceptors][request] access from storage:', access)

      if (access) {
        config.headers = config.headers ?? {}
        config.headers.Authorization = `Bearer ${access}`
      }

      return config
    },
    (error) => Promise.reject(error),
  )

  /** =====================================================================================
   *  🔹 2) Response Interceptor: access 만료 시 자동 refresh → 재요청
   * ===================================================================================== */

  let isRefreshing = false
  let refreshQueue: ((token: string) => void)[] = []

  client.interceptors.response.use(
    (response) => response,

    async (error: AxiosError) => {
      // 🔴 여기서도 InternalAxiosRequestConfig로 캐스팅
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }

      const status = error.response?.status
      console.log('[setupInterceptors][response] status:', status)

      // 401 Unauthorized + access 만료 케이스만 처리
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true // 무한 루프 방지

        const { refresh } = getStoredTokens()
        console.log('[setupInterceptors][response] refresh from storage:', refresh)

        if (!refresh) {
          // refresh 없으면 그냥 실패 + 로그인 필요
          localStorage.removeItem('nestudy-auth')
          window.location.href = '/login'
          return Promise.reject(error)
        }

        // 이미 refresh 요청 중이라면 기다렸다가 재시도
        if (isRefreshing) {
          return new Promise((resolve) => {
            refreshQueue.push((token: string) => {
              originalRequest.headers = originalRequest.headers ?? {}
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(client(originalRequest))
            })
          })
        }

        try {
          isRefreshing = true

          // CSRF 보장
          await ensureCsrf()
          const csrftoken = getCookie('csrftoken')

          // 🔥 refresh 요청 보내기
          const res = await axios.post(
            `${client.defaults.baseURL}/api/token/refresh/`,
            { refresh },
            {
              headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
              withCredentials: true,
            },
          )

          const newAccess = (res.data as any).access as string
          console.log(
            '[setupInterceptors][response] newAccess from refresh:',
            newAccess,
          )

          // LocalStorage(nestudy-auth)의 access만 갱신
          setAccessToken(newAccess)

          // 기다리고 있던 요청들 처리
          refreshQueue.forEach((callback) => callback(newAccess))
          refreshQueue = []

          // 원래 요청 다시 보내기
          originalRequest.headers = originalRequest.headers ?? {}
          originalRequest.headers.Authorization = `Bearer ${newAccess}`

          return client(originalRequest)
        } catch (refreshError) {
          console.error('❌ refresh 실패 → 로그아웃 필요', refreshError)
          localStorage.removeItem('nestudy-auth')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    },
  )
}
