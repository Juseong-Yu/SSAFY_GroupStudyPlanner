<template>
  <div class="d-flex min-vh-100">
    <!-- ✅ 왼쪽: SettingNavBar (크기/색 기존 사이드바와 동일) -->
    <SettingNavBar />

    <!-- ✅ 오른쪽: 회원정보 수정 폼 -->
    <div class="flex-grow-1 bg-white p-5">
      <div class="container" style="max-width: 1000px">
        <h3 class="fw-bold mb-4">회원정보 수정</h3>

        <div class="card shadow-sm">
          <div class="card-body p-4">
            <!-- 프로필 이미지 -->
            <div class="mb-4">
              <label class="form-label fw-semibold">프로필 이미지</label>
              <div class="d-flex align-items-center gap-3">
                <div class="rounded-circle border d-flex align-items-center justify-content-center bg-light"
                  style="width: 88px; height: 88px">
                  <!-- 프로필 이미지가 있을 때 -->
                  <img v-if="avatarPreview || form.avatar_url" :src="avatarPreview || form.avatar_url" alt="avatar"
                    class="rounded-circle" style="width: 100%; height: 100%; object-fit: cover" />

                  <!-- 기본 아이콘 -->
                  <i v-else class="bi bi-person-fill text-secondary" style="font-size: 2.5rem" />
                </div>
                <div class="d-flex flex-column gap-2">
                  <input ref="fileInputRef" class="form-control" type="file" accept="image/*" @change="onFileChange" />
                  <button v-if="avatarPreview" class="btn btn-outline-secondary btn-sm align-self-start"
                    @click="clearAvatarPreview">
                    미리보기 취소
                  </button>
                </div>
              </div>
              <div class="form-text">JPG/PNG 권장, 5MB 이하.</div>
            </div>

            <hr />

            <!-- 닉네임 / 이메일 -->
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label for="nickname" class="form-label fw-semibold">닉네임</label>
                <input id="nickname" v-model.trim="form.nickname" type="text" class="form-control" maxlength="20"
                  placeholder="닉네임" required />
              </div>

              <div class="col-md-6">
                <label for="email" class="form-label fw-semibold">이메일</label>
                <input id="email" v-model.trim="form.email" type="email" class="form-control"
                  placeholder="you@example.com" required />
              </div>
            </div>

            <!-- 비밀번호 변경 (선택) -->
            <div class="mb-2">
              <label class="form-label fw-semibold">비밀번호 변경 (선택)</label>
              <div class="row g-3">
                <div class="col-md-6">
                  <input v-model="password1" type="password" class="form-control" placeholder="새 비밀번호"
                    autocomplete="new-password" />
                </div>
                <div class="col-md-6">
                  <input v-model="password2" type="password" class="form-control" placeholder="새 비밀번호 확인"
                    autocomplete="new-password" />
                </div>
              </div>
              <div v-if="passwordError" class="text-danger small mt-2">
                {{ passwordError }}
              </div>
              <div class="form-text">비밀번호를 변경하지 않으려면 빈 칸으로 두세요.</div>
            </div>

            <!-- 오류 메시지 -->
            <div v-if="submitError" class="alert alert-danger mt-3 py-2">
              {{ submitError }}
            </div>

            <!-- 액션 버튼 -->
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button class="btn btn-outline-secondary" type="button" :disabled="submitting" @click="onCancel">
                취소
              </button>
              <button class="btn btn-primary" type="button"
                :disabled="submitting || !!passwordError || !canSubmitBasics" @click="onSubmit">
                {{ submitting ? '저장 중...' : '저장' }}
              </button>
            </div>
          </div>
        </div>


        <!-- 저장 성공 토스트 -->
        <div v-if="saved" class="toast align-items-center text-bg-success show position-fixed bottom-0 end-0 m-4"
          role="alert" aria-live="assertive" aria-atomic="true">
          <div class="d-flex">
            <div class="toast-body">프로필이 저장되었습니다.</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="saved = false"></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ✅ client를 사용하는 페이지에서는 반드시 CSRF 유틸 import 필요
 */
import SettingNavBar from '@/components/layout/SettingNavBar.vue'
import { ref, computed, onMounted } from 'vue'
import client from '@/api/client'
import { useRouter } from 'vue-router'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import { useUserStore } from '@/stores/user'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const router = useRouter()

const form = ref({
  email: '',
  nickname: '',
  avatar_url: '',
})
const password1 = ref('')
const password2 = ref('')
const passwordError = ref('')
const submitError = ref('')
const submitting = ref(false)
const saved = ref(false)
const loading = ref(false) // ✅ 추가됨

const fileInputRef = ref(null)
const avatarFile = ref(null)
const avatarPreview = ref('')
const user = useUserStore()

// ✅ 프로필 로드
const loadProfile = async () => {
  try {
    submitError.value = ''
    loading.value = true

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')
    const { data } = await client.get(`${API_BASE}/api/search/`, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken },
    })

    form.value.email = data.email || ''
    form.value.nickname = data.username || ''
    if (data.profile_img && !data.profile_img.startsWith('http')) {
      form.value.avatar_url = `${API_BASE}${data.profile_img}`
    } else {
      form.value.avatar_url = data.profile_img || ''
    }
  } catch (err) {
    console.error(err)
    submitError.value = '사용자 정보를 불러오지 못했습니다.'
    if (err?.response?.status === 401) router.push('/login')
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)

const canSubmitBasics = computed(
  () => form.value.email.trim().length > 0 && form.value.nickname.trim().length > 0,
)

const validatePasswords = () => {
  passwordError.value = ''
  if (!password1.value && !password2.value) return true
  if (password1.value.length < 8) {
    passwordError.value = '비밀번호는 8자 이상이어야 합니다.'
    return false
  }
  if (password1.value !== password2.value) {
    passwordError.value = '비밀번호가 일치하지 않습니다.'
    return false
  }
  return true
}

const onFileChange = (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  // ✅ 이미지 형식/용량 체크
  if (!file.type.startsWith('image/')) {
    submitError.value = '이미지 파일만 업로드할 수 있습니다.'
    e.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    submitError.value = '이미지 용량은 5MB 이하여야 합니다.'
    e.target.value = ''
    return
  }

  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = () => (avatarPreview.value = reader.result)
  reader.readAsDataURL(file)
}

const clearAvatarPreview = () => {
  avatarPreview.value = ''
  avatarFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}


const onSubmit = async () => {
  submitError.value = ''
  if (!validatePasswords()) return

  try {
    submitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken') || ''

    // 1) 프로필 업데이트 (FormData)
    const fd = new FormData()
    fd.append('email', form.value.email)
    fd.append('username', form.value.nickname)
    if (avatarFile.value) fd.append('profile_img', avatarFile.value)

    await client.patch(`${API_BASE}/api/update/`, fd, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken },
    })

    // 2) 비밀번호 변경 (JSON) - 비밀번호 입력이 있는 경우만
    if (password1.value && password2.value) {
      await client.post(
        `${API_BASE}/api/password/`,
        {
          // 백엔드가 요구하면 current_password도 같이 보내야 함
          // current_password: currentPassword.value,
          password: password1.value,
          new_password: password2.value,
        },
        {
          withCredentials: true,
          headers: { 'X-CSRFToken': csrftoken },
        },
      )
    }

    saved.value = true
    password1.value = ''
    password2.value = ''
    await loadProfile()
    await user.reset()
    router.push('/settings/profile')
  } catch (err) {
    console.error(err)
    const data = err?.response?.data
    if (data && typeof data === 'object') {
      const firstKey = Object.keys(data)[0]
      const msg = Array.isArray(data[firstKey]) ? data[firstKey][0] : String(data[firstKey])
      submitError.value = msg || '저장에 실패했습니다.'
    } else {
      submitError.value = '저장에 실패했습니다.'
    }
  } finally {
    submitting.value = false
  }
}


const onCancel = () => {
  router.back()
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

input:disabled {
  background-color: #f9f9f9;
}
</style>
