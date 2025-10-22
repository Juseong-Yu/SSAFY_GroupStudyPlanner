<!-- src/views/MainPage.vue -->
<template>
  <AppShell>
    <!-- ✅ 전체 화면 중앙 정렬 -->
    <div class="d-flex justify-content-center align-items-center min-vh-100">
      <img src="@/assets/wait.png" alt="Group Study Planner Logo" class="main-logo" />
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
</script>

<style scoped>
.main-logo {
  max-width: 300px; /* 로고 크기 */
  height: auto;
}
</style>
