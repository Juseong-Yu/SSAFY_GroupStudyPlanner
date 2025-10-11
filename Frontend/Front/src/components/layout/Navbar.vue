<template>
  <div class="sidebar d-flex flex-column vh-100 bg-light shadow-sm position-relative">
    <!-- 프로필 영역 -->
    <div class="profile-section d-flex align-items-center justify-content-between p-3 border-bottom position-relative">
      <div class="d-flex align-items-center">
        <img
          src="@/assets/logo.svg"
          alt="Profile"
          class="rounded-circle me-2"
          width="30"
          height="30"
        />
        <div class="fw-semibold">{{ username }}</div>
      </div>

      <!-- 닉네임 옆 드롭다운 -->
      <div class="dropdown">
        <button
          class="btn p-0 border-0 bg-transparent"
          type="button"
          id="profileDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          <i class="bi bi-three-dots-vertical fs-5 text-secondary"></i>
        </button>

        <ul
          class="dropdown-menu shadow-sm custom-dropdown"
          aria-labelledby="profileDropdown"
        >
          <li>
            <RouterLink
              to="/accounts/password-check"
              class="dropdown-item"
            >
              회원정보 수정
            </RouterLink>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li>
            <button
              class="dropdown-item text-danger"
              @click="onLogout"
            >
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
            @click="toggleMenu('manage')"
            style="cursor: pointer;"
          >
            <div><i class="bi bi-graph-up-arrow me-2"></i>관리</div>
            <i :class="isOpen.manage ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.manage" class="list-unstyled ps-4 mt-2">
            <li>
              <RouterLink to="/manage/dashboard" class="text-decoration-none text-dark">
                Dashboard
              </RouterLink>
            </li>
          </ul>
        </li>

        <li>
          <div
            class="d-flex justify-content-between align-items-center px-3 fw-semibold text-secondary"
            @click="toggleMenu('participate')"
            style="cursor: pointer;"
          >
            <div><i class="bi bi-people me-2"></i>참여</div>
            <i :class="isOpen.participate ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.participate" class="list-unstyled ps-4 mt-2">
            <li>
              <RouterLink to="/participate/dashboard" class="text-decoration-none text-dark">
                Dashboard
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const username = '주성 유'
const isOpen = ref({
  manage: true,
  participate: true,
})

const toggleMenu = (key) => {
  isOpen.value[key] = !isOpen.value[key]
}

const onLogout = async () => {
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')
    await axios.post(`${API_BASE}/accounts/logout/`, null, {
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken },
    })
    router.push('/login')
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.sidebar {
  width: 250px;
}

.profile-section:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s;
}

.dropdown-toggle::after {
  display: none !important; /* ▼ 화살표 제거 */
}

/* 🔧 드롭다운이 사이드바를 가리지 않게 오른쪽 약간 밖으로 띄움 */
.custom-dropdown {
  position: absolute;
  top: 100%;
  right: -10px; /* 사이드바 밖으로 살짝 */
  transform: translateY(2px);
  min-width: 160px;
}

/* 시각적으로 자연스럽게 */
.custom-dropdown.show {
  display: block;
}

.router-link-active {
  font-weight: 600;
  color: #0d6efd !important;
}
</style>
