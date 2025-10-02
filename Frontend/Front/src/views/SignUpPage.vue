<template>
  <div class="container vh-100 d-flex align-items-center">
    <div class="row w-100">
      <!-- 왼쪽 이미지 영역 -->
      <div class="col-lg-6 signup-image d-flex justify-content-center align-items-center">
        <img src="@/assets/signup.png" alt="스터디 이미지" class="img-fluid" style="max-width: 100%;">
      </div>

      <!-- 오른쪽 회원가입 폼 -->
      <div class="col-lg-6 col-12 d-flex align-items-center">
        <div class="signup-form-wrapper w-75">
          <h3 class="fw-bold mb-3 title-text">
            당신의 목표를 함께 이뤄줄<br/>스터디 파트너
          </h3>
          <p class="text-muted">집중을 위한 출석 관리<br/>목표 달성을 돕는 일정 알림</p>

          <!-- 소셜 로그인 버튼 -->
          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-google w-50 d-flex align-items-center justify-content-center gap-2">
              <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" width="20" height="20" />
              Google
            </button>
            <button class="btn btn-kakao w-50 d-flex align-items-center justify-content-center gap-2">
              <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/kakaotalk.svg" alt="Kakao" width="20" height="20" />
              Kakao
            </button>
          </div>

          <!-- 회원가입 폼 -->
          <form @submit.prevent="onSubmit" novalidate>
            <!-- 닉네임 -->
            <div class="mb-3">
              <label class="form-label">닉네임</label>
              <input
                v-model.trim="nickname"
                type="text"
                class="form-control"
                :class="{'is-invalid': fieldError('nickName')}"
                placeholder="닉네임 입력"
              />
              <div class="invalid-feedback" v-if="fieldError('nickName')">
                {{ fieldError('nickName') }}
              </div>
            </div>

            <!-- 이메일 -->
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input
                v-model.trim="email"
                type="email"
                class="form-control"
                :class="{'is-invalid': fieldError('email')}"
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
                :class="{'is-invalid': fieldError('password')}"
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
                :class="{'is-invalid': (!passwordsMatch && confirmPassword) || fieldError('conformPassword')}"
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
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
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

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''  // 예: http://127.0.0.1:8000

const router = useRouter()
const nickname = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agree = ref(false)
const loading = ref(false)

// 서버 에러 수신 저장용
const serverErrors = ref({})       // { field: 'message' }
const nonFieldError = ref('')      // 공통 에러/메시지

const passwordsMatch = computed(() => {
  return confirmPassword.value === '' || password.value === confirmPassword.value
})

const canSubmit = computed(() => {
  return (
    nickname.value &&
    email.value &&
    password.value &&
    confirmPassword.value &&
    passwordsMatch.value &&
    agree.value &&
    !loading.value
  )
})

// 특정 필드 에러 메시지 반환 (없으면 '')
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
    // 백엔드 스펙에 맞춰 payload 구성
    // nickName / conformPassword 키 주의!
    const payload = {
      email: email.value,
      nickName: nickname.value,
      password: password.value,
      conformPassword: confirmPassword.value,
    }

    const res = await axios.post(`${API_BASE}/users/signup`, payload, {
      headers: { 'Content-Type': 'application/json' },
      // 필요 시 withCredentials: true
    })

    // 성공 처리 (백엔드 설계에 따라 200/201 등)
    // 보통은 로그인 페이지로 이동 or 자동 로그인
    // 여기서는 로그인 페이지로 이동 예시
    router.push({ path: '/login', query: { signedup: '1' } })
  } catch (err) {
    // 에러 응답 파싱
    // 예상 형태:
    // { email: "...", nickName: "...", password: "...", conformPassword: "...", detail: "..." }
    if (err.response && err.response.data) {
      const data = err.response.data
      const mapped = {}

      // 필드별 매핑 (문자열/배열 모두 수용)
      ;['email', 'nickName', 'password', 'conformPassword'].forEach((k) => {
        if (data[k]) mapped[k] = Array.isArray(data[k]) ? data[k][0] : String(data[k])
      })

      serverErrors.value = mapped
      nonFieldError.value = data.detail ? String(data.detail) : ''
    } else {
      nonFieldError.value = '네트워크 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@media (max-width: 992px) {  /* Bootstrap lg 이하 */
  .signup-image { display: none !important; }
  .signup-form-wrapper {
    margin-left: auto;
    margin-right: auto;  /* 작은 화면에서만 중앙 정렬 */
  }
}

/* ===== Signup 버튼 ===== */
.btn-signup {
  background-color: #ffffff;
  color: #0d6efd;
  border: 1px solid #0d6efd;
  transition: background-color 0.3s ease, color 0.3s ease;
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
  transition: background-color 0.3s ease, color 0.3s ease;
}
.btn-google:hover { background-color: #f5f5f5; }

/* ===== Kakao 버튼 ===== */
.btn-kakao {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #FEE500;
  transition: background-color 0.3s ease, color 0.3s ease;
}
.btn-kakao img {
  filter: invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%);
  transition: filter 0.3s ease;
}
.btn-kakao:hover { background-color: #FEE500; color: #000000; }
.btn-kakao:hover img {
  filter: invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%);
}
</style>
