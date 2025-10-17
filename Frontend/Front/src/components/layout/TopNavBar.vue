<template>
  <nav class="navbar navbar-light bg-white border-bottom fixed-top shadow-sm topbar">
    <div class="container-fluid">
      <!-- 햄버거: 사이드바 토글 -->
      <button
        class="btn btn-outline-secondary me-2"
        type="button"
        aria-label="사이드바 열고 닫기"
        :aria-expanded="ui.sidebarOpen ? 'true' : 'false'"
        aria-controls="leftSidebar"
        @click="ui.toggleSidebar"
      >
        <i class="bi" :class="ui.sidebarOpen ? 'bi-x-lg' : 'bi-list'"></i>
      </button>

      <!-- 브랜드 / 페이지 타이틀 -->
      <span class="navbar-brand mb-0 h1">Group Study Planner</span>

      <!-- 우측 액션 영역(필요 시 채우기) -->
      <div class="d-flex align-items-center gap-2">
        <!-- 예: 알림, 프로필 등 -->
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
</style>
