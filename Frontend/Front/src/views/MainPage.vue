<!-- src/views/MainPage.vue -->
<template>
  <div class="d-flex">
    <!-- 왼쪽: Navbar -->
    <Navbar />

    <!-- 오른쪽: 본문 (지금은 빈 공간) -->
    <div class="flex-grow-1 bg-white p-4">
      <h1 class="fw-bold">메인 페이지</h1>
      <p>여기에 메인 콘텐츠가 들어갑니다.</p>
    </div>
  </div>
  
</template>

<script setup>
import Navbar from '@/components/layout/Navbar.vue'
</script>
