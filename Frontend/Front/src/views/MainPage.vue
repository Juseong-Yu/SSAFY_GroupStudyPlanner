<template>
  <div class="d-flex">
    <Navbar />

    <div class="flex-grow-1 bg-white p-4">
      <h1 class="fw-bold mb-4">메인 페이지</h1>

      <!-- ✅ 스터디 생성 카드 -->
      <div class="card shadow-sm" style="max-width: 500px">
        <div class="card-body">
          <h5 class="card-title mb-3">스터디 생성 테스트 (URLSearchParams)</h5>

          <!-- 입력 -->
          <div class="mb-3">
            <label for="studyName" class="form-label fw-semibold">스터디 이름</label>
            <input
              type="text"
              id="studyName"
              class="form-control"
              v-model="studyName"
              placeholder="예: 알고리즘 스터디"
            />
          </div>

          <!-- 버튼 -->
          <button class="btn btn-primary w-100" @click="createStudy" :disabled="loading">
            {{ loading ? '생성 중...' : '스터디 생성' }}
          </button>

          <!-- 결과 메시지 -->
          <div v-if="message" class="alert mt-3" :class="messageClass">
            {{ message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Navbar from '@/components/layout/Navbar.vue'
import axios from 'axios'
import { ref, computed } from 'vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const studyName = ref('')
const message = ref('')
const loading = ref(false)

const messageClass = computed(() =>
  message.value.includes('성공') ? 'alert-success' : 'alert-danger',
)

const createStudy = async () => {
  if (!studyName.value.trim()) {
    message.value = '스터디 이름을 입력해주세요.'
    return
  }

  try {
    loading.value = true
    message.value = ''

    // ✅ CSRF 설정
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // ✅ URLSearchParams 로 params 구성
    const params = new URLSearchParams()
    params.append('name', String(studyName.value).trim())

    // ✅ POST 요청 (params 전달)
    const res = await axios.post(`${API_BASE}/studies/create_study/`, params, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/x-www-form-urlencoded', // 꼭 지정!
      },
    })

    console.log('응답:', res.data)
    message.value = '✅ 스터디 생성 성공!'
    studyName.value = ''
  } catch (err) {
    console.error('에러 발생:', err)
    message.value = '❌ 스터디 생성 실패: 콘솔을 확인해주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
</style>
