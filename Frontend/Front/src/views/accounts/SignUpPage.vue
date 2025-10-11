<template>
  <div class="container min-vh-100 py-5 d-flex align-items-center signup-page">
    <!-- ✅ row에 gutter 추가 -->
    <div class="row w-100 g-5">
      <!-- 왼쪽 이미지 영역 -->
      <div class="col-lg-6 signup-image d-flex justify-content-center align-items-center">
        <img
          src="@/assets/signup.png"
          alt="스터디 이미지"
          class="img-fluid"
          style="max-width: 100%"
        />
      </div>

      <!-- 오른쪽 회원가입 폼 -->
      <div class="col-lg-6 col-12 d-flex align-items-center">
        <div class="signup-form-wrapper">
          <h3 class="fw-bold mb-3 title-text">당신의 목표를 함께 이뤄줄<br />스터디 파트너</h3>
          <p class="text-muted">집중을 위한 출석 관리<br />목표 달성을 돕는 일정 알림</p>

          <!-- 소셜 로그인 버튼 -->
          <div class="d-flex gap-2 mb-3">
            <button
              class="btn btn-google w-50 d-flex align-items-center justify-content-center gap-2"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                width="20"
                height="20"
              />
              Sign Up with Google
            </button>
            <button
              class="btn btn-kakao w-50 d-flex align-items-center justify-content-center gap-2"
            >
              <img
                src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kakaotalk.svg"
                alt="Kakao"
                width="20"
                height="20"
              />
              Sign Up with Kakao
            </button>
          </div>

          <!-- 회원가입 폼 -->
          <form @submit.prevent="onSubmit" novalidate>
            <!-- 닉네임 -->
            <div class="mb-3">
              <label class="form-label">닉네임</label>
              <input
                v-model.trim="username"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': fieldError('username') }"
                placeholder="닉네임 입력"
              />
              <div class="invalid-feedback" v-if="fieldError('username')">
                {{ fieldError('username') }}
              </div>
            </div>

            <!-- 이메일 -->
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input
                v-model.trim="email"
                type="email"
                class="form-control"
                :class="{ 'is-invalid': fieldError('email') }"
                placeholder="이메일 입력"
              />
              <div class="invalid-feedback" v-if="fieldError('email')">
                {{ fieldError('email') }}
              </div>
            </div>

            <!-- 비밀번호 -->
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input
                v-model="password"
                type="password"
                class="form-control"
                :class="{ 'is-invalid': fieldError('password') }"
                placeholder="비밀번호 입력"
              />
              <div class="invalid-feedback" v-if="fieldError('password')">
                {{ fieldError('password') }}
              </div>
            </div>

            <!-- 비밀번호 확인 (스펙의 conformPassword로 전송) -->
            <div class="mb-3">
              <label class="form-label">Confirm Password</label>
              <input
                v-model="confirmPassword"
                type="password"
                class="form-control"
                :class="{
                  'is-invalid':
                    (!passwordsMatch && confirmPassword) || fieldError('conformPassword'),
                }"
                placeholder="비밀번호 확인 입력"
              />
              <div class="invalid-feedback" v-if="!passwordsMatch && confirmPassword">
                비밀번호가 일치하지 않습니다.
              </div>
              <div class="invalid-feedback" v-else-if="fieldError('conformPassword')">
                {{ fieldError('conformPassword') }}
              </div>
            </div>

            <div class="form-check mb-3">
              <input type="checkbox" class="form-check-input" id="terms" v-model="agree" />
              <label class="form-check-label" for="terms">
                I accept the terms &amp; condition
              </label>
            </div>

            <!-- 서버 공통 에러 -->
            <div class="alert alert-danger py-2" v-if="nonFieldError" role="alert">
              {{ nonFieldError }}
            </div>

            <button type="submit" class="btn btn-signup w-100" :disabled="!canSubmit || loading">
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              SIGN UP
            </button>
          </form>

          <!-- 로그인 링크 -->
          <p class="text-center mt-3">
            이미 계정이 있으신가요?
            <RouterLink to="/login" class="link-primary fw-semibold">로그인</RouterLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agree = ref(false)
const loading = ref(false)

const serverErrors = ref({})
const nonFieldError = ref('')

const passwordsMatch = computed(() => {
  return confirmPassword.value === '' || password.value === confirmPassword.value
})

const canSubmit = computed(() => {
  return (
    username.value &&
    email.value &&
    password.value &&
    confirmPassword.value &&
    passwordsMatch.value &&
    agree.value &&
    !loading.value
  )
})

const fieldError = (field) => {
  if (!serverErrors.value) return ''
  return serverErrors.value[field] || ''
}

const resetErrors = () => {
  serverErrors.value = {}
  nonFieldError.value = ''
}

const onSubmit = async () => {
  if (!canSubmit.value) return
  resetErrors()
  loading.value = true

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const params = new URLSearchParams()
    // Django UserCreationForm 기본 필드
    params.append('username', username.value)
    params.append('email', email.value)
    params.append('password1', password.value)
    params.append('password2', confirmPassword.value)

    await axios.post(`${API_BASE}/accounts/signup/`, params, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    // ✅ 회원가입 성공 시 로그인 페이지로 이동
    router.push('/login')
  } catch (err) {
    console.error(err)
    // 필요하면 에러 처리 로직 추가
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 컨테이너를 화면 높이 이상으로 늘릴 수 있게 하고, 넘치면 스크롤 */
.signup-page {
  overflow-y: auto;
}

/* 폼 폭: 모바일에서 넉넉하게, 데스크탑에서는 가운데  */
.signup-form-wrapper {
  width: 100%;
  max-width: 560px; /* 모바일/태블릿에서 읽기 좋은 폭 */
  margin-left: auto;
  margin-right: auto;
}
@media (min-width: 992px) {
  .signup-form-wrapper {
    max-width: 640px; /* 데스크탑에서 살짝 더 넓게 */
    /* ✅ 이미지와 폼 사이 추가 여백 */
    margin-left: 2rem;
  }
}

/* lg 이하에서 좌측 이미지 제거 → 폼 높이 확보 */
@media (max-width: 992px) {
  .signup-image {
    display: none !important;
  }
}

/* ===== Signup 버튼 ===== */
.btn-signup {
  background-color: #ffffff;
  color: #0d6efd;
  border: 1px solid #0d6efd;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}
.btn-signup:hover {
  background-color: #e6f0ff;
  border: 1px solid #0d6efd;
  color: #0d6efd;
}

/* ===== Google 버튼 ===== */
.btn-google {
  background-color: #ffffff;
  color: #444444;
  border: 1px solid #dddddd;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}
.btn-google:hover {
  background-color: #f5f5f5;
}

/* ===== Kakao 버튼 ===== */
.btn-kakao {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #fee500;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}
.btn-kakao img {
  filter: invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%);
  transition: filter 0.3s ease;
}
.btn-kakao:hover {
  background-color: #fee500;
  color: #000000;
}
.btn-kakao:hover img {
  filter: invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%);
}
</style>
