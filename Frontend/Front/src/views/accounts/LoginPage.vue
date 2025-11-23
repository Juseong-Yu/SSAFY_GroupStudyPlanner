<template>
  <div class="container min-vh-100 py-5 d-flex align-items-center login-page">
    <!-- row에 g-5 적용 -->
    <div class="row w-100 g-5">
      <!-- 왼쪽 이미지 영역 -->
      <div class="col-lg-6 login-image d-none d-lg-flex justify-content-center align-items-center">
        <img
          src="@/assets/login.png"
          alt="로그인 이미지"
          class="img-fluid"
          style="max-width: 80%"
        />
      </div>

      <!-- 오른쪽 로그인 폼 -->
      <div class="col-lg-6 col-12 d-flex align-items-center">
        <div class="login-form-wrapper">
          <h3 class="fw-bold mb-3 title-text">다시 오신 것을 환영합니다!</h3>

          <!-- 소셜 로그인 버튼 -->
          <div class="d-flex gap-2 mb-4">
            <button
              class="btn btn-google w-50 d-flex align-items-center justify-content-center gap-2"
              @click="onSocial('google')"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                width="20"
                height="20"
              />
              Log In with Google
            </button>
            <button
              class="btn btn-kakao w-50 d-flex align-items-center justify-content-center gap-2"
              @click="onSocial('kakao')"
            >
              <img
                src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kakaotalk.svg"
                alt="Kakao"
                width="20"
                height="20"
              />
              Log In with Kakao
            </button>
          </div>

          <!-- 로그인 폼 -->
          <form @submit.prevent="onSubmit" novalidate>
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
              <div class="pw-wrap position-relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="password"
                  class="form-control"
                  :class="{ 'is-invalid': fieldError('password') }"
                  placeholder="비밀번호 입력"
                />
                <button
                  type="button"
                  class="btn btn-link btn-eye-absolute"
                  @click="showPassword = !showPassword"
                  :aria-label="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
                  tabindex="-1"
                >
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
              <div class="invalid-feedback d-block" v-if="fieldError('password')">
                {{ fieldError('password') }}
              </div>
            </div>

            <!-- Remember me -->
            <div class="form-check mb-3">
              <input
                class="form-check-input"
                type="checkbox"
                id="rememberMe"
                v-model="rememberMe"
              />
              <label class="form-check-label" for="rememberMe">Remember me</label>
            </div>

            <!-- 서버 공통 에러 -->
            <div class="alert alert-danger py-2" v-if="nonFieldError" role="alert">
              {{ nonFieldError }}
            </div>

            <button type="submit" class="btn btn-login w-100" :disabled="!canSubmit || loading">
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              LOG IN
            </button>
          </form>

          <!-- 회원가입 링크 -->
          <p class="text-center mt-3">
            아직 회원가입 안하셨나요?
            <RouterLink to="/signup" class="link-primary fw-semibold">SIGN UP</RouterLink>
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
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)

const serverErrors = ref({})
const nonFieldError = ref('')

const canSubmit = computed(() => {
  return email.value && password.value && !loading.value
})

const fieldError = (field) => {
  if (!serverErrors.value) return ''
  return serverErrors.value[field] || ''
}

const resetErrors = () => {
  serverErrors.value = {}
  nonFieldError.value = ''
}

const onSocial = (provider) => {
  console.log('social login:', provider)
}

// ✅ onSubmit: form-urlencoded + CSRF + username/password (순수 JS)
const onSubmit = async () => {
  if (!canSubmit.value || loading.value) return
  resetErrors()
  loading.value = true

  try {
    // CSRF 쿠키 준비
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // Django가 바로 읽는 포맷으로 전송
    const params = new URLSearchParams()
    params.set('username', String(email.value || '').trim()) // 이메일을 username으로 사용
    params.set('password', String(password.value || ''))

    await axios.post(`${API_BASE}/accounts/login/`, params, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    router.push({ path: '/main' })
  } catch (err) {
    // 에러 매핑 (username/password/non_field_errors/detail 우선순위)
    if (err && err.response && err.response.data) {
      const data = err.response.data
      const mapped = {}
      ;['username', 'password', 'non_field_errors', 'detail'].forEach(function (k) {
        if (data[k]) mapped[k] = Array.isArray(data[k]) ? data[k][0] : String(data[k])
      })
      serverErrors.value = {
        username: mapped.username,
        password: mapped.password,
      }
      nonFieldError.value = mapped.non_field_errors || mapped.detail || '로그인에 실패했습니다.'
    } else {
      nonFieldError.value = '네트워크 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  overflow-y: auto;
}

.login-form-wrapper {
  width: 100%;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}
@media (min-width: 992px) {
  .login-form-wrapper {
    max-width: 640px;
    margin-left: 2rem; /* 이미지와 폼 간격 확보 */
  }
}

/* 비밀번호 입력칸 */
.pw-wrap .form-control {
  padding-right: 2.75rem; /* 아이콘 자리 확보 */
}

.btn-eye-absolute {
  position: absolute;
  top: 50%;
  right: 0.625rem;
  transform: translateY(-50%);
  height: 2.375rem;
  width: 2.375rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  text-decoration: none;
  padding: 0;
}

.btn-eye-absolute:hover {
  color: #0d6efd;
}

.pw-wrap:focus-within .form-control {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

/* 버튼 스타일 */
.btn-login {
  background-color: #ffffff;
  color: #0d6efd;
  border: 1px solid #0d6efd;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}
.btn-login:hover {
  background-color: #e6f0ff;
  color: #0d6efd;
  border: 1px solid #0d6efd;
}

/* 소셜 버튼 */
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

/* 작은 화면에서는 좌측 이미지 제거 */
@media (max-width: 992px) {
  .login-image {
    display: none !important;
  }
}
</style>
