<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
      <div class="spinner-border mb-3" role="status"></div>
      <p class="text-muted">연결 중입니다…</p>
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

/* ✅ sessionStorage key */
const DISCORD_PENDING_KEY = 'nestudy-discord-pending'

type PendingDiscord = {
  studyId: number
  createdAt: number
}

function readPending(): PendingDiscord | null {
  const raw = sessionStorage.getItem(DISCORD_PENDING_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as PendingDiscord
  } catch {
    return null
  }
}

onMounted(async () => {
  const { code, guild_id, permissions } = route.query

  // 1️⃣ 필수 query 검증
  if (!code || !guild_id) {
    router.replace('/')
    return
  }

  // 2️⃣ sessionStorage에서 studyId 복원
  const pending = readPending()
  if (!pending) {
    // 스터디 컨텍스트 유실
    alert('스터디 정보를 찾을 수 없습니다. 다시 시도해주세요.')
    router.replace('/')
    return
  }

  // (선택) 유효 시간 제한 (예: 10분)
  if (Date.now() - pending.createdAt > 10 * 60 * 1000) {
    sessionStorage.removeItem(DISCORD_PENDING_KEY)
    alert('연결 시간이 초과되었습니다. 다시 시도해주세요.')
    router.replace(`/studies/${pending.studyId}`)
    return
  }

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // 3️⃣ 복원한 studyId로 callback 호출
    await client.get(`${API_BASE}/studies/${pending.studyId}/discord/bot/callback/`, {
      params: {
        guild_id,
        permissions,
      },
      withCredentials: true,
      headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
    })

    // ✅ 성공 시 pending 제거
  } catch (e) {
    console.error('discord bot callback failed', e)
  } finally {
    sessionStorage.removeItem(DISCORD_PENDING_KEY)
    // 4️⃣ 스터디 페이지로 복귀
    router.replace(`/studies/${pending.studyId}`)
  }
})
</script>
