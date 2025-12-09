<template>
  <div class="container min-vh-100 py-3 d-flex align-items-center signup-page">
    <!-- 흰색 카드 래퍼 -->
    <div class="auth-surface w-100 p-4 p-lg-5">
      <div class="row w-100 g-5">
        <!-- 왼쪽 이미지 -->
        <div class="col-lg-6 signup-image d-flex justify-content-center align-items-center">
          <img
            src="@/assets/signup.png"
            alt="회원 가입 이미지"
            class="img-fluid"
            style="max-width: 80%"
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
                <img src="@/assets/kakao_icon.png" alt="Kakao" width="20" height="20" />
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
                  :class="{ 'is-invalid': passwordError || fieldError('password') }"
                  placeholder="비밀번호 입력"
                />
                <div class="invalid-feedback" v-if="passwordError">
                  {{ passwordError }}
                </div>
                <div class="invalid-feedback" v-else-if="fieldError('password')">
                  {{ fieldError('password') }}
                </div>
              </div>

              <!-- 비밀번호 확인 -->
              <div class="mb-3">
                <label class="form-label">Confirm Password</label>
                <input
                  v-model="confirmPassword"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid':
                      (!passwordsMatch && confirmPassword) || fieldError('password2'),
                  }"
                  placeholder="비밀번호 확인 입력"
                />
                <div class="invalid-feedback" v-if="!passwordsMatch && confirmPassword">
                  비밀번호가 일치하지 않습니다.
                </div>
                <div class="invalid-feedback" v-else-if="fieldError('password2')">
                  {{ fieldError('password2') }}
                </div>
              </div>

              <!-- 약관 -->
              <div class="form-check mb-3">
                <input type="checkbox" class="form-check-input" id="terms" v-model="agree" />
                <label class="form-check-label" for="terms">
                  I accept the
                  <button
                    type="button"
                    class="btn btn-link text-primary p-0 align-baseline ms-1"
                    data-bs-toggle="modal"
                    data-bs-target="#termsModal"
                  >
                    Terms &amp; Conditions
                  </button>
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
  </div>

  <!-- ✅ 약관 모달 -->
  <div class="modal fade" id="termsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header">
          <h5 class="modal-title fw-bold">서비스 이용약관</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div class="terms-content" v-html="termsHtml"></div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
          <button type="button" class="btn btn-outline-primary" data-bs-dismiss="modal">
            확인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'
import termsMd from '@/legal/terms_ko.md?raw'
import { marked } from 'marked'

// 마크다운 옵션 (AI 느낌 제거용)
marked.setOptions({ mangle: false, headerIds: false })
const termsHtml = ref(marked.parse(termsMd))

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
const passwordError = ref('')

// ✅ 비밀번호 유효성 검증
const validatePassword = (value) => {
  passwordError.value = ''

  if (value.length < 8) {
    passwordError.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return false
  }
  if (/^\d+$/.test(value)) {
    passwordError.value = '비밀번호는 숫자만으로 구성될 수 없습니다.'
    return false
  }
  const banned = ['password', '12345678', 'qwerty', 'abc123', 'asdfgh', '11111111']
  if (banned.includes(value.toLowerCase())) {
    passwordError.value = '너무 단순한 비밀번호입니다.'
    return false
  }
  if (username.value && value.toLowerCase().includes(username.value.toLowerCase())) {
    passwordError.value = '비밀번호에 닉네임이 포함되어 있습니다.'
    return false
  }
  const emailPrefix = email.value.split('@')[0]?.toLowerCase()
  if (emailPrefix && value.toLowerCase().includes(emailPrefix)) {
    passwordError.value = '비밀번호에 이메일 일부가 포함되어 있습니다.'
    return false
  }
  return true
}

watch(password, (val) => {
  if (val) validatePassword(val)
})

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
    !loading.value &&
    !passwordError.value
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

  if (!validatePassword(password.value)) return

  loading.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const params = new URLSearchParams()
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

    router.push('/login')
  } catch (err) {
    console.error('Signup error:', err)
    if (err.response) {
      const data = err.response.data
      if (typeof data === 'object') {
        for (const [key, value] of Object.entries(data)) {
          if (key === 'non_field_errors' || key === 'detail') {
            nonFieldError.value = Array.isArray(value) ? value.join(', ') : value
          } else {
            serverErrors.value[key] = Array.isArray(value) ? value.join(', ') : value
          }
        }
      } else {
        nonFieldError.value = '회원가입 중 오류가 발생했습니다.'
      }
    } else {
      nonFieldError.value = '서버와의 통신 중 문제가 발생했습니다.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signup-page {
  overflow-y: auto;
  background: #f6f8fb;
}
.title-text {
  color: #0f172a;
}

.signup-page p {
  color: #475569;
}

/* 이미지 투명도 */
.login-image img {
  opacity: 0.8;
}

/* 카드형 흰 배경 박스 */
.auth-surface {
  background: #ffffff;
  border: 1px solid #e5e7eb; /* 슬레이트 200 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border-radius: 20px;

  min-height: calc(100vh - 3rem); /* 화면 기반 최소 높이 통일 */
  display: flex;
  flex-direction: column;
  justify-content: center; /* 내부 폼을 수직 중앙 정렬 */
}


.signup-form-wrapper {
  width: 100%;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}
@media (min-width: 992px) {
  .signup-form-wrapper {
    max-width: 640px;
    margin-left: 2rem;
  }
}
@media (max-width: 992px) {
  .signup-image {
    display: none !important;
  }
}

/* 약관 본문 */
.terms-content {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', 'Apple SD Gothic Neo',
    'Malgun Gothic', 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.92rem;
  line-height: 1.65;
  color: #2b2f36;
  max-width: 68ch;
  margin: 0 auto;
}

.terms-content h1,
.terms-content h2,
.terms-content h3,
.terms-content h4 {
  font-weight: 600;
  letter-spacing: 0.1px;
  color: #1f2328;
  margin: 1rem 0 0.5rem;
}

.terms-content h1 {
  font-size: 1.05rem;
}
.terms-content h2 {
  font-size: 1.02rem;
}
.terms-content h3 {
  font-size: 1rem;
}
.terms-content h4 {
  font-size: 0.98rem;
}

.terms-content p,
.terms-content ul,
.terms-content ol {
  margin: 0.5rem 0;
}

.terms-content ul,
.terms-content ol {
  padding-left: 1.1rem;
}
.terms-content li + li {
  margin-top: 0.25rem;
}

.terms-content hr {
  border: none;
  border-top: 1px solid #eceff3;
  margin: 0.9rem 0;
}

.terms-content a {
  color: #0d6efd;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.terms-content a:hover {
  color: #0a58ca;
}

/* 모달 */
.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: #24292f;
}
.modal-body {
  padding: 1.25rem 1.25rem 1rem;
}

/* 버튼 스타일 */
.btn-signup {
  border: 1px solid #94a3b8;     /* slate-400 */
  color: #334155;                /* slate-700 */
  background-color: transparent;
  border-radius: 999px;
  padding: 0.6rem 1rem;
  font-weight: 600;
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
}

.btn-signup:hover {
  background-color: rgba(148, 163, 184, 0.08);
  border-color: #64748b;
}



/* 소셜 로그인 버튼 */
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

.btn-kakao {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #fee500;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}
.btn-kakao:hover {
  background-color: #fee500;
  color: #000000;
}
</style>
