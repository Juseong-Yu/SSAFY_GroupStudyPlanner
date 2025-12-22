<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
      <div class="spinner-border mb-3" role="status"></div>
      <p class="text-muted">연결 중입니다…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const code = new URLSearchParams(window.location.search).get('code')

  if (!code) {
    error.value = '디스코드 코드가 없습니다.'
    loading.value = false
    return
  }

  try {
    const res = await auth.oauthLoginWithDiscord(code)
    if (res.type === 'login') {
      router.replace('/main')
    } else if (res.type === 'register') {
      router.replace('/accounts/OauthInfo')
    }
  } catch (e: any) {
    console.error(e)
    error.value =
      e?.response?.data?.detail ?? e?.response?.data?.message ?? '디스코드 로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped></style>
