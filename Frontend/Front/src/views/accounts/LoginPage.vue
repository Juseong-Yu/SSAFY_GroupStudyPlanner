<template>
  <div class="container min-vh-100 py-3 d-flex align-items-center login-page">
    <!-- 🔶 중앙 카드 래퍼 -->
    <div class="auth-surface w-100 p-3 p-lg-4">
      <div class="row w-100 g-5">
        <!-- 왼쪽 이미지 -->
        <div
          class="col-lg-6 login-image d-none d-lg-flex justify-content-center align-items-center"
        >
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
            <h3 class="fw-bold mb-3 title-text">
              다시 오신 것을 환영합니다!
            </h3>

            <!-- 소셜 로그인 -->
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
                class="btn btn-discord w-50 d-flex align-items-center justify-content-center gap-2"
                @click="onSocial('discord')"
              >
                <i class="bi bi-discord fs-5"></i>
                Log In with Discord
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
                    :aria-label="
                      showPassword ? '비밀번호 숨기기' : '비밀번호 보기'
                    "
                    tabindex="-1"
                  >
                    <i
                      :class="
                        showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'
                      "
                    ></i>
                  </button>
                </div>
                <div
                  class="invalid-feedback d-block"
                  v-if="fieldError('password')"
                >
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
                <label class="form-check-label" for="rememberMe">
                  Remember me
                </label>
              </div>

              <!-- 서버 에러 -->
              <div
                class="alert alert-danger py-2"
                v-if="nonFieldError"
                role="alert"
              >
                {{ nonFieldError }}
              </div>

              <!-- 로그인 버튼 -->
              <button
                type="submit"
                class="btn btn-login w-100"
                :disabled="!canSubmit || loading"
              >
                <span
                  v-if="loading"
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                LOG IN
              </button>
            </form>

            <p class="text-center mt-3">
              아직 회원가입 안 하셨나요?
              <RouterLink to="/signup" class="link-primary fw-semibold">
                SIGN UP
              </RouterLink>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { fetchAllStores } from '@/stores/fetchAllStores'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'

type SocialProvider = 'google' | 'discord'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)

const serverErrors = ref<Record<string, string | undefined>>({})
const nonFieldError = ref('')

const canSubmit = computed(
  () => !!email.value && !!password.value && !loading.value,
)

const fieldError = (field: 'email' | 'password') =>
  serverErrors.value[field] || ''

const resetErrors = () => {
  serverErrors.value = {}
  nonFieldError.value = ''
}

const onSocial = async (provider: SocialProvider) => {
  try {
    if (provider === 'google') {
      console.warn('Google OAuth endpoint not wired yet')
      return
    }

    // ✅ 디스코드 "로그인 링크 반환" 엔드포인트
    const { data } = await axios.get<{ auth_url: string }>(
      `${API_BASE}/api/login_with_discord/`,
      { withCredentials: true },
    )

    if (!data?.auth_url) throw new Error('auth_url missing')

    // ✅ 디스코드 인증 페이지로 이동
    window.location.assign(data.auth_url)
  } catch (err) {
    console.error('[discord social login start] failed', err)
    // 필요하면 UI 에러로 연결
    // nonFieldError.value = '디스코드 로그인 시작에 실패했습니다.'
  }
}

const onSubmit = async () => {
  if (!canSubmit.value || loading.value) return

  resetErrors()
  loading.value = true

  try {
    await auth.login(email.value.trim(), password.value)
    await fetchAllStores()
    router.push('/main')
  } catch (err: any) {
    const data = err?.response?.data
    if (data) {
      const mapped: Record<string, string> = {}

      ;['email', 'password', 'non_field_errors', 'detail'].forEach((k) => {
        if (data[k])
          mapped[k] = Array.isArray(data[k]) ? data[k][0] : String(data[k])
      })

      serverErrors.value = {
        email: mapped.email,
        password: mapped.password,
      }

      nonFieldError.value =
        mapped.non_field_errors ||
        mapped.detail ||
        '로그인에 실패했습니다.'
    } else {
      nonFieldError.value = '네트워크 오류가 발생했습니다.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  background: #f6f8fb;
  overflow-y: auto;
}

.auth-surface {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border-radius: 20px;
  min-height: calc(100vh - 3rem);
  display: flex;
  justify-content: center;
}

.login-form-wrapper {
  width: 100%;
  max-width: 560px;
  margin: auto;
}

@media (min-width: 992px) {
  .login-form-wrapper {
    max-width: 640px;
    margin-left: 2rem;
  }
}

.login-image img {
  opacity: 0.8;
}

.title-text {
  color: #0f172a;
}

.pw-wrap .form-control {
  padding-right: 2.75rem;
}

.btn-eye-absolute {
  position: absolute;
  top: 50%;
  right: 0.625rem;
  transform: translateY(-50%);
  width: 2.375rem;
  height: 2.375rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.btn-eye-absolute:hover {
  color: #0d6efd;
}

.btn-login {
  border: 1px solid #94a3b8;
  color: #334155;
  background-color: transparent;
  border-radius: 999px;
  padding: 0.6rem 1rem;
  font-weight: 600;
}

.btn-login:hover {
  background-color: rgba(148, 163, 184, 0.08);
  border-color: #64748b;
}

/* Google */
.btn-google {
  background-color: #ffffff;
  color: #444;
  border: 1px solid #ddd;
}

.btn-google:hover {
  background-color: #f5f5f5;
}

/* Discord */
.btn-discord {
  background-color: #5865f2;
  color: #ffffff;
  border: 1px solid #5865f2;
}

.btn-discord:hover {
  background-color: #4752c4;
  border-color: #4752c4;
  color: #ffffff;
}

@media (max-width: 992px) {
  .login-image {
    display: none !important;
  }
}
</style>
