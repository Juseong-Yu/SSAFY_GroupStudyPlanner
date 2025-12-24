<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100">
    <div class="text-center">
      <div class="spinner-border mb-3" role="status"></div>
      <p class="text-muted" v-if="loading">연결 중입니다…</p>
      <p class="text-danger" v-else-if="error">{{ error }}</p>
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

    // ✅ TS18048: res possibly undefined 방어
    if (!res || !res.type) {
      throw new Error('디스코드 로그인 응답이 비어있습니다.')
    }

    if (res.type === 'login') {
      router.replace('/main')
    } else if (res.type === 'register') {
      router.replace('/accounts/OauthInfo')
    } else {
      // ✅ 예상 못한 type 방어
      throw new Error(`알 수 없는 로그인 타입: ${String(res.type)}`)
    }
  } catch (e: any) {
    console.error(e)
    error.value =
      e?.response?.data?.detail ??
      e?.response?.data?.message ??
      e?.message ??
      '디스코드 로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped></style>
