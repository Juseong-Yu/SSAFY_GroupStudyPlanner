<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
      <div class="spinner-border mb-3" role="status"></div>
      <p class="text-muted">디스코드 서버 연결 중입니다…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const route = useRoute()
const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE_URL as string

/**
 * /discord/connect/?code=...&guild_id=...&permissions=...
 * → 그대로 백엔드 callback으로 전달
 */
onMounted(async () => {
  const { code, guild_id, permissions, state } = route.query

  if (!code || !guild_id) {
    // 잘못된 접근
    router.replace('/')
    return
  }

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.get(
      `${API_BASE}/studies/${state}/discord/bot/callback/`,
      {
        params: {
          code,
          guild_id,
          permissions,
        },
        withCredentials: true,
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
      },
    )
  } catch (e) {
    console.error('discord bot callback failed', e)
  } finally {
    // 👉 스터디 페이지로 복귀
    router.replace(`/studies/${state}`)
  }
})
</script>
