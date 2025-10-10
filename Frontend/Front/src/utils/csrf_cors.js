import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

export const ensureCsrf = async () => {
  if (!getCookie('csrftoken')) {
    await axios.get(`${API_BASE}/accounts/csrf/`, { withCredentials: true })
  }
}
