<template>
  <!-- 오버레이 (모바일 전용) -->
  <div v-if="ui.sidebarOpen" class="sidebar-backdrop d-lg-none" @click="ui.closeSidebar"></div>

  <!-- 왼쪽 슬라이딩 사이드바 -->
  <aside
    id="leftSidebar"
    class="sidebar d-flex flex-column bg-light shadow-sm position-fixed"
    :class="{ 'is-open': ui.sidebarOpen }"
    @keydown.esc="onEscape"
    aria-label="왼쪽 네비게이션 바"
  >
    <!-- 프로필 영역 -->
    <div
      class="profile-section d-flex align-items-center justify-content-between p-3 border-bottom"
    >
      <div class="d-flex align-items-center">
        <!-- ★ 프로필 이미지: 로딩/미설정 대비 -->
        <template v-if="user.loading">
          <span class="placeholder rounded-circle me-2" style="width: 30px; height: 30px"></span>
          <div class="placeholder col-4" style="height: 1rem"></div>
        </template>
        <template v-else>
          <img
            :src="avatarSrc"
            alt="Profile"
            class="rounded-circle me-2 border"
            width="30"
            height="30"
            style="object-fit: cover"
          />
          <div class="fw-semibold">{{ usernameDisplay }}</div>
        </template>
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
            <!-- ★ 로그아웃: 스토어 액션 호출 -->
            <button
              class="dropdown-item text-danger"
              @click="handleLogoutClick"
              :disabled="user.loading"
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
            @click="toggleAccordion('manage')"
            style="cursor: pointer"
          >
            <div><i class="bi bi-clipboard-data me-2"></i>관리</div>
            <i :class="isOpen.manage ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.manage" class="list-unstyled ps-4 mt-2">
            <li>
              <RouterLink
                to="/manage/dashboard"
                class="text-decoration-none text-dark"
                @click="maybeCloseOnMobile"
              >
                Dashboard
              </RouterLink>
            </li>
          </ul>
        </li>

        <li>
          <div
            class="d-flex justify-content-between align-items-center px-3 fw-semibold text-secondary"
            @click="toggleAccordion('participate')"
            style="cursor: pointer"
          >
            <div><i class="bi bi-people-fill me-2"></i>참여</div>
            <i :class="isOpen.participate ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </div>
          <ul v-if="isOpen.participate" class="list-unstyled ps-4 mt-2">
            <li>
              <RouterLink
                to="/participate/dashboard"
                class="text-decoration-none text-dark"
                @click="maybeCloseOnMobile"
              >
                Dashboard
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user' // ★ 사용자 스토어

// axios를 직접 쓰지 않더라도, 이 컴포넌트에선 X. (logout은 store가 처리)
// 규칙상 axios 쓰는 파일에서만 ensureCsrf/getCookie import 필요

const ui = useUiStore()
const user = useUserStore()

// 아코디언 상태
const isOpen = ref({ manage: true, participate: true })
const toggleAccordion = (key: 'manage' | 'participate') => {
  isOpen.value[key] = !isOpen.value[key]
}

/** 드롭다운 */
const menuOpen = ref(false)
const dropdownRoot = ref<HTMLElement | null>(null)
const toggleProfileMenu = () => (menuOpen.value = !menuOpen.value)
const closeMenu = () => (menuOpen.value = false)
const onClickOutside = (e: MouseEvent) => {
  if (!dropdownRoot.value) return
  if (!dropdownRoot.value.contains(e.target as Node)) closeMenu()
}
const onEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    closeMenu()
    if (ui.sidebarOpen) ui.closeSidebar()
  }
}

function maybeCloseOnMobile() {
  // 모바일에서는 메뉴 클릭 시 사이드바 닫기
  if (!ui.isLgUp) ui.closeSidebar()
}

/** ★ 프로필 표시용 계산 */
const usernameDisplay = computed(() => user.profile?.nickname ?? '로그인 필요')
const defaultAvatar = '/default-avatar.png' // public 폴더에 간단한 기본 이미지 하나 둬도 좋아요
const avatarSrc = computed(() => user.profile?.avatar_url || defaultAvatar)

/** ★ 로그아웃: 스토어 액션 호출 */
const handleLogoutClick = async () => {
  closeMenu()
  try {
    await user.logout()
  } catch (e) {
    // 실패해도 logout()에서 클라이언트 정리를 보장함
    console.error(e)
  }
}

onMounted(() => {
  // ★ 여기가 중요: 최초 진입 시 유저 정보 1회 로드(중복 호출 안전)
  user.loadIfNeeded()

  document.addEventListener('click', onClickOutside, { capture: true })
  document.addEventListener('keydown', onEscape)
  // 레이아웃 변수
  document.documentElement.style.setProperty('--sidebar-width', '250px')
  document.documentElement.style.setProperty('--gap', '20px')
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, { capture: true })
  document.removeEventListener('keydown', onEscape)
})
</script>

<style scoped>
/* 사이드바: 기본 닫힘 */
.sidebar {
  width: var(--sidebar-width, 250px);
  top: var(--topbar-height, 56px); /* 탑바 아래부터 시작 */
  left: 0;
  z-index: 1070;
  transform: translateX(-100%);
  transition: transform 0.25s ease-in-out;
  will-change: transform;
  height: calc(100vh - var(--topbar-height, 56px));
}
.sidebar.is-open {
  transform: translateX(0);
}

/* 오버레이 (모바일 전용) */
.sidebar-backdrop {
  position: fixed;
  inset: var(--topbar-height, 56px) 0 0 0; /* 탑바를 가리지 않게 */
  background: rgba(33, 37, 41, 0.45);
  z-index: 1030;
}

/* 드롭다운/호버 */
.profile-section {
  overflow: visible;
  position: relative;
}
.profile-section:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s;
}
.router-link-active {
  font-weight: 600;
  color: #0d6efd !important;
}
</style>
