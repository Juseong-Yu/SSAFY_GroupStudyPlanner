<template>
  <div class="container py-5">
    <div class="card shadow-sm">
      <div class="card-body p-4">
        <h5 class="fw-bold mb-2">디스코드 로그인 처리 중...</h5>

        <p v-if="loading" class="text-muted mb-0">
          잠시만 기다려 주세요.
        </p>

        <div v-else-if="error" class="alert alert-danger mb-0" role="alert">
          {{ error }}
        </div>

        <div v-else class="alert alert-success mb-0" role="alert">
          로그인 성공! 이동 중...
        </div>
      </div>
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
    if (res.type === 'login'){
      router.replace('/main')
    }else if (res.type ==='register'){
      router.replace('/accounts/OauthInfo')
    }
  } catch (e: any) {
    console.error(e)
    error.value =
      e?.response?.data?.detail ??
      e?.response?.data?.message ??
      '디스코드 로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped></style>
