<template>
  <div class="container min-vh-100 py-5 d-flex align-items-center signup-page">
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

            <!-- 약관 -->
            <div class="form-check mb-3">
              <input type="checkbox" class="form-check-input" id="terms" v-model="agree" />
              <label class="form-check-label" for="terms">
                I accept the
                <!-- ✅ 더 명확한 버튼 -->
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

  <!-- ✅ 약관 모달 -->
  <div class="modal fade" id="termsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header">
          <h5 class="modal-title fw-bold">Terms &amp; Conditions</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <!-- Markdown 내용 렌더 -->
          <div class="terms-content" v-html="termsHtml"></div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal">확인</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import termsMd from '@/legal/terms_ko.md?raw' // ✅ 약관 Markdown 가져오기
import { marked } from 'marked' // ✅ 마크다운 파서 설치 필요

const termsHtml = ref(marked.parse(termsMd)) // 마크다운 → HTML 변환

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
  font-size: 0.95rem;
  line-height: 1.7;
}
.terms-content h2,
.terms-content h3 {
  margin-top: 1rem;
  font-weight: 600;
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

/* ===== 소셜 버튼 ===== */
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
