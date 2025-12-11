<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="card shadow-sm p-4" style="max-width: 400px; width: 100%;">
      <h4 class="fw-bold mb-3 text-center">비밀번호 확인</h4>
      <p class="text-muted small text-center mb-4">
        회원정보를 수정하기 위해 비밀번호를 한 번 더 입력해주세요.
      </p>

      <form @submit.prevent="onSubmit">
        <div class="mb-3">
          <label for="password" class="form-label fw-semibold">비밀번호</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="form-control"
            placeholder="비밀번호를 입력하세요"
            required
          />
        </div>

        <div v-if="error" class="alert alert-danger py-2 small">
          {{ error }}
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100"
          :disabled="loading"
        >
          {{ loading ? '확인 중...' : '확인' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import client from '@/api/client'
import { useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const router = useRouter()

const password = ref('')
const error = ref('')
const loading = ref(false)

const onSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const response = await client.post(
      `${API_BASE}/accounts/password-check/`,
      { password: password.value },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      }
    )

    if (response.status === 200) {
      // ✅ 비밀번호 확인 성공 시 회원정보 수정 페이지로 이동
      router.push('/accounts/update')
    }
  } catch (err) {
    error.value = '비밀번호가 올바르지 않습니다.'
  } finally {
    loading.value = false
  }
}
</script>
