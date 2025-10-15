<!-- AppSidebar.vue -->
<template>
  <div class="app-shell">
    <!-- ▷ 토글 버튼 -->
    <button
      class="btn btn-light shadow toggle-sidebar-btn smart-pos"
      :class="{ 'is-open': sidebarOpen }"
      :aria-expanded="sidebarOpen ? 'true' : 'false'"
      aria-controls="leftSidebar"
      aria-label="사이드바 열고 닫기"
      @click="toggleSidebar"
    >
      <i class="bi" :class="sidebarOpen ? 'bi-x-lg' : 'bi-list'"></i>
    </button>

    <!-- ▷ 오버레이 (lg 미만에서만) -->
    <div
      v-if="sidebarOpen"
      class="sidebar-backdrop d-lg-none"
      @click="closeSidebar"
    ></div>

    <!-- ▷ 왼쪽 슬라이딩 사이드바 -->
    <aside
      id="leftSidebar"
      class="sidebar d-flex flex-column vh-100 bg-light shadow-sm position-fixed"
      :class="{ 'is-open': sidebarOpen }"
      @keydown.esc="closeSidebar"
    >
      <!-- 프로필 영역 -->
      <div class="profile-section d-flex align-items-center justify-content-between p-3 border-bottom">
        <div class="d-flex align-items-center">
          <img src="@/assets/logo.svg" alt="Profile" class="rounded-circle me-2" width="30" height="30" />
          <div class="fw-semibold">{{ username }}</div>
        </div>

        <!-- 닉네임 옆 드롭다운 (Vue 제어) -->
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
    </aside>

    <!-- ▷ 메인 콘텐츠
         - lg 이상에서만 사이드바 열림 여부에 따라 패딩 적용
         - 닫히면 padding-left: 0 → "페이지가 전체를 차지"
    -->
    <main
      class="main-content"
      :class="{ 'with-sidebar': isLgUp && sidebarOpen }"
    >
      <slot />
    </main>
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

/** 반응형 상태 (lg 기준) */
const isLgUp = ref(window.innerWidth >= 992)

/** 사이드바 열고 닫기 (lg 이상 기본 오픈) */
const sidebarOpen = ref(isLgUp.value)
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const closeSidebar = () => { sidebarOpen.value = false }
const openSidebar  = () => { sidebarOpen.value = true }

/** 드롭다운 */
const menuOpen = ref(false)
const dropdownRoot = ref(null)
const toggleProfileMenu = () => { menuOpen.value = !menuOpen.value }
const closeMenu = () => { menuOpen.value = false }
const onClickOutside = (e) => {
  if (!dropdownRoot.value) return
  if (!dropdownRoot.value.contains(e.target)) closeMenu()
}
const onEscape = (e) => {
  if (e.key === 'Escape') {
    closeMenu()
    if (sidebarOpen.value) closeSidebar()
  }
}

/** 반응형 핸들링 */
const handleResize = () => {
  isLgUp.value = window.innerWidth >= 992
  if (isLgUp.value) openSidebar()
  else closeSidebar()
}

onMounted(() => {
  document.addEventListener('click', onClickOutside, { capture: true })
  document.addEventListener('keydown', onEscape)
  window.addEventListener('resize', handleResize)

  // CSS 변수
  const topbarHeight = 56 // 실제 상단 네비 높이
  document.documentElement.style.setProperty('--topbar-height', `${topbarHeight}px`)
  document.documentElement.style.setProperty('--sidebar-width', '250px')
  document.documentElement.style.setProperty('--gap', '20px')
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, { capture: true })
  document.removeEventListener('keydown', onEscape)
  window.removeEventListener('resize', handleResize)
})

/** 로그아웃 */
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
  try { await onLogout() } catch (e) { console.error(e) }
}
</script>

<style scoped>
.app-shell { min-height: 100vh; }

/* 사이드바: 기본 닫힘 */
.sidebar {
  width: var(--sidebar-width, 250px);
  top: 0;
  left: 0;
  z-index: 1070;
  transform: translateX(-100%);
  transition: transform 0.25s ease-in-out;
  will-change: transform;
}
.sidebar.is-open { transform: translateX(0); }

/* 메인: 부드러운 좌측 패딩 전환 */
.main-content {
  min-height: 100vh;
  transition: padding-left 0.25s ease-in-out;
}
/* lg 이상일 때만 사이드바가 열려 있으면 패딩 적용 */
@media (min-width: 992px) {
  .main-content.with-sidebar {
    padding-left: var(--sidebar-width, 250px);
  }
}

/* 드롭다운/호버 */
.profile-section { overflow: visible; position: relative; }
.profile-section:hover { background-color: #f8f9fa; transition: background-color 0.2s; }
.router-link-active { font-weight: 600; color: #0d6efd !important; }

/* ▷ 스마트 위치 토글 버튼 (모바일: 우하단, 데스크톱: 탑바 아래 10px) */
.toggle-sidebar-btn {
  z-index: 1060;
  border-radius: 9999px;
  padding: .5rem .65rem;
  background-color: white;
  border-style: solid;
  border-color: gray;
}
.smart-pos {
  position: fixed;
  right: var(--gap, 20px);
  bottom: var(--gap, 20px);
  transition: left .25s ease, top .25s ease, right .25s ease, bottom .25s ease, transform .25s ease;
}
@media (min-width: 992px) {
  .smart-pos {
    top: 10px;
    bottom: auto;
    right: auto;
    left: var(--gap, 20px);
  }
  .smart-pos.is-open {
    left: calc(var(--sidebar-width, 250px) + var(--gap, 20px));
  }
}

/* 오버레이 (모바일 전용) */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(33, 37, 41, 0.45);
  z-index: 1030;
}

/* 접근성 */
.toggle-sidebar-btn:focus { box-shadow: 0 0 0 0.2rem rgba(13,110,253,.25); }
@media (prefers-reduced-motion: reduce) {
  .smart-pos { transition: none; }
}
</style>
