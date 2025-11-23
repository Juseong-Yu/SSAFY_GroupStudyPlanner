<!-- src/views/settings/ProfilePage.vue -->
<template>
  <div class="d-flex min-vh-100">
    <SettingNavBar />

    <div class="flex-grow-1 bg-white p-5">
      <div class="container" style="max-width: 800px">
        <h3 class="fw-bold mb-4">회원정보</h3>

        <div class="card shadow-sm">
          <div class="card-body p-4">
            <!-- 프로필 이미지 -->
            <div class="mb-4">
              <label class="form-label fw-semibold">프로필 이미지</label>

              <div v-if="loading" class="placeholder-glow d-flex align-items-center gap-3">
                <span class="placeholder rounded-circle" style="width: 112px; height: 112px"></span>
                <span class="placeholder col-3"></span>
              </div>

              <div v-else class="d-flex align-items-center gap-3">
                <!-- ✅ 이미지 or 기본 Bootstrap 아이콘 -->
                <div
                  class="rounded-circle border d-flex justify-content-center align-items-center bg-light"
                  style="width: 112px; height: 112px"
                >
                  <i
                    v-if="!profile.avatar_url"
                    class="bi bi-person-fill text-secondary"
                    style="font-size: 64px"
                  ></i>
                  <img
                    v-else
                    :src="profile.avatar_url"
                    alt="avatar"
                    class="rounded-circle"
                    width="112"
                    height="112"
                    style="object-fit: cover"
                  />
                </div>
              </div>
            </div>

            <hr />

            <!-- 닉네임 / 이메일 (읽기 전용 텍스트) -->
            <dl class="row g-3 mb-3 align-items-center">
              <dt class="col-md-3">
                <span class="form-label fw-semibold mb-0 d-block">닉네임</span>
              </dt>
              <dd class="col-md-9 mb-0">
                <div v-if="loading" class="placeholder-glow">
                  <span class="placeholder col-6"></span>
                </div>
                <div v-else class="read-text">
                  {{ profile.nickname || '닉네임 없음' }}
                </div>
              </dd>

              <dt class="col-md-3">
                <span class="form-label fw-semibold mb-0 d-block">이메일</span>
              </dt>
              <dd class="col-md-9 mb-0">
                <div v-if="loading" class="placeholder-glow">
                  <span class="placeholder col-8"></span>
                </div>
                <div v-else class="read-text">
                  {{ profile.email || '이메일 없음' }}
                </div>
              </dd>
            </dl>

            <!-- ✅ 프로필 편집 버튼 -->
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button
                class="btn btn-outline-primary"
                :disabled="loading"
                @click="openPasswordModal"
              >
                프로필 편집
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ✅ 비밀번호 확인 모달 -->
    <div
      class="modal fade"
      id="passwordModal"
      tabindex="-1"
      aria-labelledby="passwordModalLabel"
      aria-hidden="true"
      ref="modalRef"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold" id="passwordModalLabel">비밀번호 확인</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>

          <div class="modal-body">
            <p class="mb-3 text-muted small">회원정보를 수정하려면 비밀번호를 입력해주세요.</p>

            <input
              type="password"
              class="form-control"
              v-model="password"
              placeholder="비밀번호를 입력하세요"
              autocomplete="current-password"
              @keyup.enter="onConfirmPassword"
            />

            <div v-if="errorMsg" class="text-danger small mt-2">
              {{ errorMsg }}
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="loadingCheck"
              @click="onConfirmPassword"
            >
              {{ loadingCheck ? '확인 중...' : '확인' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import SettingNavBar from '@/components/layout/SettingNavBar.vue'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'
import { useRouter } from 'vue-router'
import * as bootstrap from 'bootstrap'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const router = useRouter()

const loading = ref(true)
const error = ref('')
const profile = ref({
  email: '',
  nickname: '',
  avatar_url: '',
})

// 모달 관련
const modalRef = ref(null)
let modalInstance = null
const password = ref('')
const errorMsg = ref('')
const loadingCheck = ref(false)

onMounted(() => {
  modalInstance = new bootstrap.Modal(modalRef.value)
  loadProfile()
})

const openPasswordModal = () => {
  password.value = ''
  errorMsg.value = ''
  modalInstance.show()
}

// 🔐 비밀번호 확인 로직 (API 연결 가능)
const onConfirmPassword = async () => {
  if (!password.value.trim()) {
    errorMsg.value = '비밀번호를 입력해주세요.'
    return
  }

  try {
    loadingCheck.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const params = new URLSearchParams()
    params.set('password', String(password.value).trim())

    const res = await axios.post(
      `${API_BASE}/accounts/check_password/`,
      params,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    )

    if (res.status === 200) {
      errorMsg.value = ''
      modalInstance.hide()
      router.push('/settings/update')
    }
  } catch (e) {
    // 서버 응답을 보고 메시지를 더 구체화
    const msg = e?.response?.data?.error || '비밀번호가 올바르지 않습니다.'
    errorMsg.value = msg
    console.error('check_password error:', e?.response?.status, e?.response?.data)
  } finally {
    loadingCheck.value = false
  }
}

// ✅ 프로필 로드
const loadProfile = async () => {
  try {
    error.value = ''
    loading.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')
    const { data } = await axios.get(`${API_BASE}/accounts/search/`, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken },
    })

    profile.value.email = data.email || ''
    profile.value.nickname = data.username || ''
    if (data.profile_img && !data.profile_img.startsWith('http')) {
      profile.value.avatar_url = `${API_BASE}${data.profile_img}`
    } else {
      profile.value.avatar_url = data.profile_img || ''
    }
  } catch (e) {
    console.error(e)
    error.value = '사용자 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.flex-grow-1 {
  overflow-y: auto;
}

.card {
  border: none;
  border-radius: 12px;
}

/* 모달 커스텀 */
.modal-content {
  border-radius: 12px;
}
.modal-header {
  border-bottom: none;
}
.modal-footer {
  border-top: none;
}
.read-text {
  line-height: 1.9;
  /* 필요하면 미세 톤업: color: #212529; */
}
</style>
