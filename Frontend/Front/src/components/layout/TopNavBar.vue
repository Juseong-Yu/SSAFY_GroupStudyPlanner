<!-- src/components/layout/TopNavBar.vue -->
<template>
  <nav class="navbar navbar-light bg-white border-bottom fixed-top shadow-sm topbar">
    <div class="container-fluid">
      <!-- 왼쪽: 햄버거 버튼 + 로고 + 타이틀 -->
      <div class="d-flex align-items-center gap-2">
        <!-- 햄버거 버튼 -->
        <button
          class="btn btn-outline-secondary"
          type="button"
          aria-label="사이드바 열고 닫기"
          :aria-expanded="ui.sidebarOpen ? 'true' : 'false'"
          aria-controls="leftSidebar"
          @click="ui.toggleSidebar"
        >
          <i class="bi" :class="ui.sidebarOpen ? 'bi-x-lg' : 'bi-list'"></i>
        </button>

        <!-- 🔥 로고 + 텍스트를 RouterLink로 감싸기 -->
        <RouterLink
          to="/main"
          class="d-flex align-items-center gap-2 text-decoration-none"
        >
          <!-- 로고 -->
          <img
            src="@/assets/logo.png"
            alt="logo"
            width="40"
            height="40"
            class="me-1"
          />

          <!-- 타이틀 -->
          <span class="navbar-brand mb-0 h1 fs-5 fw-semibold text-dark">
            Group Study Planner
          </span>
        </RouterLink>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useUiStore } from '@/stores/ui'
import { RouterLink } from 'vue-router'

const ui = useUiStore()

onMounted(() => {
  const topbarHeight = 56
  document.documentElement.style.setProperty('--topbar-height', `${topbarHeight}px`)
  window.addEventListener('resize', ui.handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', ui.handleResize)
})
</script>

<style scoped>
.topbar {
  height: var(--topbar-height, 56px);
}

/* 링크 스타일이 기본 bootstrap에 잡히지 않도록 */
a {
  color: inherit;
}
a:hover {
  color: inherit;
  text-decoration: none;
}

/* 버튼 hover 효과 */
button.btn {
  transition: background-color 0.2s, color 0.2s;
}
</style>
