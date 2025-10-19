<!-- src/components/layout/TopNavBar.vue -->
<template>
  <nav class="navbar navbar-light bg-white border-bottom fixed-top shadow-sm topbar">
    <div class="container-fluid">
      <!-- 왼쪽: 햄버거 버튼 + 로고 + 타이틀 -->
      <div class="d-flex align-items-center gap-2">
        <!-- 햄버거: 사이드바 토글 -->
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

        <!-- 로고 -->
        <img
          src="@/assets/logo.png "
          alt="logo"
          width="40"
          height="40"
          class="me-1"
        />

        <!-- 타이틀 -->
        <span class="navbar-brand mb-0 h1 fs-5 fw-semibold">Group Study Planner</span>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

onMounted(() => {
  // 상단바 높이를 CSS 변수로 노출 (사이드/메인 여백 계산에 사용)
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

/* 로고와 텍스트가 수평으로 잘 정렬되도록 */
.navbar-brand {
  font-weight: 600;
  color: #212529;
}

/* 버튼 hover 효과 부드럽게 */
button.btn {
  transition: background-color 0.2s, color 0.2s;
}
</style>
