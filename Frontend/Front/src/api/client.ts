// src/api/client.ts
import axios from 'axios'
import { setupInterceptors } from './setupInterceptors'

const API_BASE = import.meta.env.VITE_API_BASE_URL as string

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
})

setupInterceptors(client)

export default client
