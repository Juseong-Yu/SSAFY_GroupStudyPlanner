import type {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios'
import axios from 'axios'
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

  if (partial.access !== undefined) {
    stored.access = partial.access
  }
  if (partial.refresh !== undefined) {
    stored.refresh = partial.refresh
  }

  localStorage.setItem('nestudy-auth', JSON.stringify(stored))
}

export function setupInterceptors(client: AxiosInstance) {
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const csrftoken = getCookie('csrftoken')
      if (csrftoken) {
        config.headers = config.headers ?? {}
        config.headers['X-CSRFToken'] = csrftoken
      }

      const { access } = getStoredTokens()
      console.log('[setupInterceptors][request] access from storage:', access)

      if (access) {
        config.headers = config.headers ?? {}
        config.headers.Authorization = `Bearer ${access}`
      }

      return config
    },
    (error) => Promise.reject(error),
  )

  let isRefreshing = false
  let refreshQueue: ((token: string) => void)[] = []

  client.interceptors.response.use(
    (response) => response,

    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }

      const status = error.response?.status
      console.log('[setupInterceptors][response] status:', status)

      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        const { refresh } = getStoredTokens()
        console.log('[setupInterceptors][response] refresh from storage:', refresh)

        if (!refresh) {
          localStorage.removeItem('nestudy-auth')
          window.location.href = '/login'
          return Promise.reject(error)
        }

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

          console.log(
            '[setupInterceptors][response] newAccess from refresh:',
            newAccess,
          )
          console.log(
            '[setupInterceptors][response] newRefresh from refresh:',
            newRefresh,
          )

          setTokens({
            access: newAccess,
            refresh: newRefresh ?? refresh,
          })

          refreshQueue.forEach((callback) => callback(newAccess))
          refreshQueue = []

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
