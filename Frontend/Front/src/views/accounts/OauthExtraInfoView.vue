<!-- src/views/accounts/OAuthExtraInfoView.vue -->
<template>
  <div class="container min-vh-100 py-3 d-flex align-items-center signup-page">
    <div class="auth-surface w-100 p-4 p-lg-5">
      <div class="row w-100 g-5">
        <!-- 왼쪽 이미지 (원하면 유지) -->
        <div
          class="col-lg-6 signup-image d-flex justify-content-center align-items-center"
        >
          <img
            src="@/assets/oauth.png"
            alt="추가정보 입력"
            class="img-fluid"
            style="max-width: 80%"
          />
        </div>

        <!-- 오른쪽 -->
        <div class="col-lg-6 col-12 d-flex align-items-center">
          <div class="signup-form-wrapper">
            <h3 class="fw-bold mb-3 title-text">
              소셜 로그인 완료!<br />추가정보만 입력하면 끝
            </h3>
            <p class="text-muted">
              스터디 참여를 위해 닉네임/약관 동의가 필요해요.
            </p>

            <!-- OAuth 프리필 카드 -->
            <div class="card border-0 shadow-sm mb-3" v-if="prefillLoaded">
              <div class="card-body d-flex align-items-center gap-3">
                <div>
                  <img
                    v-if="prefill.avatar_url"
                    :src="prefill.avatar_url"
                    alt="avatar"
                    class="rounded-circle border"
                    width="44"
                    height="44"
                    style="object-fit: cover"
                  />
                  <div
                    v-else
                    class="rounded-circle border d-flex align-items-center justify-content-center bg-light"
                    style="width: 44px; height: 44px"
                  >
                    <i class="bi bi-person-fill text-secondary"></i>
                  </div>
                </div>

                <div class="flex-grow-1">
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge" :class="providerBadgeClass">
                      {{ providerLabel }}
                    </span>
                    <span class="fw-semibold">
                      {{ prefill.display_name || prefill.provider_user_id || '사용자' }}
                    </span>
                  </div>
                  <div class="text-muted small">
                    {{ prefill.email || '이메일 정보가 없습니다.' }}
                  </div>
                </div>

                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  :disabled="loading"
                  @click="loadPrefill"
                >
                  새로고침
                </button>
              </div>
            </div>

            <form @submit.prevent="onSubmit" novalidate>
              <!-- 이메일(가능하면 readonly) -->
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  v-model.trim="form.email"
                  type="email"
                  class="form-control"
                  :readonly="!!prefill.email"
                  :disabled="!!prefill.email"
                />
                <div class="form-text">
                  소셜에서 이메일이 오면 수정 불가로 처리해도 돼요.
                </div>
              </div>

              <!-- 닉네임 -->
              <div class="mb-3">
                <label class="form-label">닉네임</label>
                <input
                  v-model.trim="form.username"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': fieldError('username') }"
                  placeholder="서비스에서 사용할 닉네임"
                  maxlength="20"
                />
                <div class="invalid-feedback" v-if="fieldError('username')">
                  {{ fieldError('username') }}
                </div>
              </div>

              <!-- 선택: 비밀번호 설정 -->
              <div class="mb-2">
                <button
                  type="button"
                  class="btn btn-link p-0 text-decoration-none"
                  @click="showPassword = !showPassword"
                >
                  <i
                    class="bi"
                    :class="showPassword ? 'bi-chevron-up' : 'bi-chevron-down'"
                  ></i>
                  <span class="ms-1">비밀번호도 설정하기 (선택)</span>
                </button>
                <div class="text-muted small mt-1">
                  나중에 이메일/비밀번호 로그인도 열어두고 싶으면 설정해.
                </div>
              </div>

              <div v-if="showPassword" class="mb-3">
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input
                    v-model="form.password"
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

                <div class="mb-0">
                  <label class="form-label">Confirm Password</label>
                  <input
                    v-model="form.password_confirm"
                    type="password"
                    class="form-control"
                    :class="{
                      'is-invalid':
                        (form.password_confirm && !passwordsMatch) ||
                        fieldError('password_confirm'),
                    }"
                    placeholder="비밀번호 확인"
                  />
                  <div class="invalid-feedback" v-if="form.password_confirm && !passwordsMatch">
                    비밀번호가 일치하지 않습니다.
                  </div>
                  <div
                    class="invalid-feedback"
                    v-else-if="fieldError('password_confirm')"
                  >
                    {{ fieldError('password_confirm') }}
                  </div>
                </div>
              </div>

              <!-- 약관 -->
              <div class="form-check mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="terms"
                  v-model="form.agree"
                />
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

              <div class="alert alert-danger py-2" v-if="nonFieldError" role="alert">
                {{ nonFieldError }}
              </div>

              <!-- ✅ 버튼 1개: 가입 완료 -->
              <button
                type="submit"
                class="btn btn-login w-100"
                :disabled="!canSubmit || loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" />
                가입 완료
              </button>

              <!-- ✅ 링크 형태: 로그인 페이지로 돌아가기 -->
              <div class="text-center mt-3">
                <router-link to="/login" class="login-back-link">
                  이미 계정이 있나요? 로그인으로 돌아가기
                </router-link>
              </div>
            </form>
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
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" />
        </div>
        <div class="modal-body">
          <div class="terms-content" v-html="termsHtml"></div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
          <button type="button" class="btn btn-outline-primary" data-bs-dismiss="modal">확인</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import termsMd from '@/legal/terms_ko.md?raw'
import { marked } from 'marked'

marked.setOptions({ mangle: false, headerIds: false })
const termsHtml = ref(marked.parse(termsMd))
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || ''
const route = useRoute()
const router = useRouter()

/**
 * ✅ 백엔드가 OAuth 로그인 후 세션/쿠키로 "임시 상태"를 들고 있고,
 * 이 API가 프리필 정보를 내려주는 형태를 추천
 */
interface OAuthPrefill {
  provider: string // 'discord' | 'google' | 'github' | ...
  provider_user_id: string | null
  email: string | null
  display_name: string | null
  avatar_url: string | null
  needs_extra_info: boolean
}

const prefill = ref<OAuthPrefill>({
  provider: (route.query.provider as string) || 'oauth',
  provider_user_id: null,
  email: null,
  display_name: null,
  avatar_url: null,
  needs_extra_info: true,
})

const prefillLoaded = ref(false)
const loading = ref(false)
const serverErrors = ref<Record<string, string>>({})
const nonFieldError = ref('')
const showPassword = ref(false)
const passwordError = ref('')

const form = ref({
  email: '',
  username: '',
  agree: false,
  password: '',
  password_confirm: '',
})

const providerLabel = computed(() => {
  const p = (prefill.value.provider || '').toLowerCase()
  if (p === 'google') return 'Google'
  if (p === 'github') return 'GitHub'
  if (p === 'discord') return 'Discord'
  if (p === 'kakao') return 'Kakao'
  if (p === 'naver') return 'Naver'
  return 'OAuth'
})

const providerBadgeClass = computed(() => {
  // Bootstrap 배지 색상만으로 통일 (디자인 간단하게)
  const p = (prefill.value.provider || '').toLowerCase()
  if (p === 'google') return 'bg-danger'
  if (p === 'github') return 'bg-dark'
  if (p === 'discord') return 'bg-primary'
  if (p === 'kakao') return 'bg-warning text-dark'
  if (p === 'naver') return 'bg-success'
  return 'bg-secondary'
})

const fieldError = (field: string) => serverErrors.value?.[field] || ''
const resetErrors = () => {
  serverErrors.value = {}
  nonFieldError.value = ''
  passwordError.value = ''
}

const validatePassword = () => {
  passwordError.value = ''
  if (!showPassword.value) return true
  if (!form.value.password) {
    passwordError.value = '비밀번호를 입력해주세요.'
    return false
  }
  if (form.value.password.length < 8) {
    passwordError.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return false
  }
  return true
}

const passwordsMatch = computed(() => {
  if (!showPassword.value) return true
  return (
    form.value.password_confirm === '' ||
    form.value.password === form.value.password_confirm
  )
})

const canSubmit = computed(() => {
  const baseOk = !!form.value.username && !!form.value.agree && !loading.value
  if (!showPassword.value) return baseOk
  return (
    baseOk &&
    !!form.value.password &&
    !!form.value.password_confirm &&
    passwordsMatch.value &&
    !passwordError.value
  )
})

/**
 * ✅ 프리필 로드
 * GET /api/oauth/prefill/
 */
const loadPrefill = async () => {
  resetErrors()
  loading.value = true
  try {
    const { data } = await axios.get<OAuthPrefill>(`${API_BASE}/api/oauth/prefill/`, {
      withCredentials: true,
    })

    prefill.value = data
    prefillLoaded.value = true

    // ✅ 이미 추가정보가 필요 없으면 로그인 페이지로
    if (data.needs_extra_info === false) {
      router.replace('/login')
      return
    }

    // ✅ 폼 프리필
    form.value.email = data.email ?? ''
    form.value.username = data.display_name ?? ''
  } catch (err: any) {
    console.error('[oauth prefill] failed', err)
    nonFieldError.value =
      err?.response?.data?.detail ||
      '추가정보를 불러오지 못했습니다. 소셜 로그인 상태를 확인해주세요.'
  } finally {
    loading.value = false
  }
}

onMounted(loadPrefill)

/**
 * ✅ 가입 완료
 * POST /api/oauth/complete_signup/
 */
const onSubmit = async () => {
  if (!canSubmit.value) return
  resetErrors()
  if (!validatePassword()) return
  if (!passwordsMatch.value) return

  loading.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const payload: Record<string, any> = {
      email: form.value.email,
      username: form.value.username,
      agree: form.value.agree,
    }

    if (showPassword.value) {
      payload.password = form.value.password
      payload.password_confirm = form.value.password_confirm
    }

    await axios.post(`${API_BASE}/api/oauth/complete_signup/`, payload, {
      withCredentials: true,
      headers: {
        ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
        'Content-Type': 'application/json',
      },
    })

    // ✅ 가입 완료 후 로그인 페이지로 이동
    router.replace('/login')
  } catch (err: any) {
    console.error('[oauth complete] failed', err)
    const data = err?.response?.data
    if (data && typeof data === 'object') {
      for (const [key, value] of Object.entries(data as Record<string, any>)) {
        const msg = Array.isArray(value) ? value.join(', ') : String(value)
        if (key === 'non_field_errors' || key === 'detail') nonFieldError.value = msg
        else serverErrors.value[key] = msg
      }
    } else {
      nonFieldError.value = '가입 완료 처리 중 오류가 발생했습니다.'
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

.auth-surface {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  border-radius: 20px;
  min-height: calc(100vh - 3rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
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

.title-text {
  color: #0f172a;
}

/* ✅ 요청한 버튼 스타일 */
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

/* ✅ 링크처럼 보이는 로그인 이동 */
.login-back-link {
  font-size: 0.9rem;
  color: #64748b;
  text-decoration: none;
}

.login-back-link:hover {
  text-decoration: underline;
  color: #334155;
}
</style>
