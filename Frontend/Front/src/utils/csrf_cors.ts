import axios from 'axios'

const API_BASE: string = import.meta.env.VITE_API_BASE_URL || ''

/**
 * 특정 이름의 쿠키 값을 반환
 */
export const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()!.split(';').shift() || null
  }
  return null
}

/**
 * CSRF 토큰이 없으면 Django에서 새로 받아오는 함수
 */
export const ensureCsrf = async (): Promise<void> => {
  //const csrf = getCookie('csrftoken')
  // if (!csrf) {
  //   await axios.get(`${API_BASE}/api/csrf/`, {
  //     withCredentials: true,
  //   })
  // }
}
