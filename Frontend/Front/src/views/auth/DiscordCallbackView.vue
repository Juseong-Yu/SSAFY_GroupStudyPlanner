<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref<string>('')

const API_BASE = import.meta.env.VITE_API_BASE_URL as string

onMounted(async () => {
  const code = route.query.code as string | undefined
  const state = route.query.state as string | undefined // ✅ 반드시 쓰는 걸 추천

  if (!code) {
    error.value = 'Discord code가 없습니다.'
    loading.value = false
    return
  }

  try {
    //await ensureCsrf()
    //const csrftoken = getCookie('csrftoken')

    // ✅ 백엔드로 "마무리" 요청 (여기서 Authorization 헤더는 인터셉터가 붙여줘야 함)
    await client.post(
      `${API_BASE}/api/auth/discord/callback/?code=${code}`,
      { code, state },
      {
        withCredentials: true,
      },
    )

    // 성공 후 원하는 페이지로
    router.replace('/settings/profile') // 예시
  } catch (e: any) {
    console.error(e)
    error.value = e?.response?.data?.detail ?? '디스코드 연동 실패'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
      <div class="spinner-border mb-3" role="status"></div>
      <p class="text-muted">연결 중입니다…</p>
    </div>
  </div>
</template>
