<template>
  <div class="sidebar d-flex flex-column vh-100 bg-light shadow-sm position-relative">
    <!-- 프로필 영역 -->
    <div class="profile-section d-flex align-items-center justify-content-between p-3 border-bottom">
      <div class="d-flex align-items-center">
        <img src="@/assets/logo.svg" alt="Profile" class="rounded-circle me-2" width="30" height="30" />
        <div class="fw-semibold">{{ username }}</div>
      </div>

      <!-- 닉네임 옆 드롭다운 (Vue 제어 방식) -->
      <div class="dropdown" ref="dropdownRoot">
        <button
          class="btn p-0 border-0 bg-transparent"
          type="button"
          id="profileDropdown"
          :aria-expanded="menuOpen ? 'true' : 'false'"
          aria-haspopup="true"
          @click.stop="toggleProfileMenu"
        >
          <i class="bi bi-three-dots-vertical fs-5 text-secondary"></i>
        </button>

        <ul
          class="dropdown-menu dropdown-menu-end shadow-sm"
          aria-labelledby="profileDropdown"
          :class="{ show: menuOpen }"
        >
          <li>
            <RouterLink to="/settings/profile" class="dropdown-item" @click="closeMenu">
              설정
            </RouterLink>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li>
            <button class="dropdown-item text-danger" @click="handleLogoutClick">
              로그아웃
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- 메뉴 리스트 -->
    <div class="menu-section flex-grow-1 mt-3">
      <ul class="list-unstyled">
        <li class="mb-3">
          <div
            class="d-flex justify-content-between align-items-center px-3 fw-semibold text-secondary"
            @click="toggleAccordion('manage')"
            style="cursor: pointer;"
          >
            <div><i class="bi bi-clipboard-data me-2"></i>관리</div>
            <i :class="isOpen.manage ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.manage" class="list-unstyled ps-4 mt-2">
            <li><RouterLink to="/manage/dashboard" class="text-decoration-none text-dark">Dashboard</RouterLink></li>
          </ul>
        </li>

        <li>
          <div
            class="d-flex justify-content-between align-items-center px-3 fw-semibold text-secondary"
            @click="toggleAccordion('participate')"
            style="cursor: pointer;"
          >
            <div><i class="bi bi-people-fill me-2"></i>참여</div>
            <i :class="isOpen.participate ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.participate" class="list-unstyled ps-4 mt-2">
            <li><RouterLink to="/participate/dashboard" class="text-decoration-none text-dark">Dashboard</RouterLink></li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const username = '주성 유'
const isOpen = ref({ manage: true, participate: true })
const toggleAccordion = (key) => { isOpen.value[key] = !isOpen.value[key] }

/** ▼ 프로필 드롭다운: Vue 제어 */
const menuOpen = ref(false)
const dropdownRoot = ref(null)

const toggleProfileMenu = () => {
  menuOpen.value = !menuOpen.value
}
const closeMenu = () => {
  menuOpen.value = false
}
const onClickOutside = (e) => {
  if (!dropdownRoot.value) return
  if (!dropdownRoot.value.contains(e.target)) closeMenu()
}
const onEscape = (e) => {
  if (e.key === 'Escape') closeMenu()
}

onMounted(() => {
  document.addEventListener('click', onClickOutside, { capture: true })
  document.addEventListener('keydown', onEscape)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, { capture: true })
  document.removeEventListener('keydown', onEscape)
})

/** ▼ 로그아웃 */
const onLogout = async () => {
  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')
  await axios.post(`${API_BASE}/accounts/logout/`, null, {
    withCredentials: true,
    headers: { 'X-CSRFToken': csrftoken },
  })
  router.push('/login')
}
const handleLogoutClick = async () => {
  closeMenu()
  try {
    await onLogout()
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.sidebar { width: 250px; }

/* 드롭다운 잘림 방지 */
.profile-section { overflow: visible; position: relative; }

/* 호버 효과 */
.profile-section:hover { background-color: #f8f9fa; transition: background-color 0.2s; }

/* 활성 라우트 강조 */
.router-link-active { font-weight: 600; color: #0d6efd !important; }
</style>
