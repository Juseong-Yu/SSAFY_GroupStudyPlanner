<template>
  <div class="app-shell">
    <TopNavbar />

    <Sidebar />

    <!-- 메인 -->
    <main class="main-content" :class="{ 'with-sidebar': ui.isLgUp && ui.sidebarOpen }">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import TopNavbar from '@/components/layout/TopNavBar.vue'
import Sidebar from '@/components/layout/Navbar.vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

/* 메인: 탑바 높이만큼 상단 여백 */
.main-content {
  min-height: 100vh;
  padding-top: var(--topbar-height, 56px);
  transition: padding-left 0.25s ease-in-out;
}

/* lg 이상일 때만 사이드바가 열려 있으면 좌측 패딩 적용 */
@media (min-width: 992px) {
  .main-content.with-sidebar {
    padding-left: var(--sidebar-width, 250px);
  }
}
</style>
