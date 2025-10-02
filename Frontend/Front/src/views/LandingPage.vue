<template>
  <main class="landing d-flex align-items-center justify-content-center text-center">
    <div>
      <h1 class="display-3 fw-bold landing-title">Study On</h1>
      <p class="text-muted mt-2">당신의 스터디를 더 효율적으로</p>

      <div class="mt-4 d-flex gap-3 justify-content-center">
  <RouterLink to="/signup" class="btn btn-outline-secondary btn-auth">
    회원 가입
  </RouterLink>
  <RouterLink to="/login" class="btn btn-outline-secondary btn-auth">
    로그인
  </RouterLink>
</div>

    </div>
  </main>
</template>

<script setup>
// 랜딩은 로직 없음
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');
/* 화면 정중앙 배치 */
.landing {
  min-height: 100vh;
}

.btn-auth {
  min-width: 120px;   /* 원하는 고정 너비 */
  padding: 0.6rem 1rem;
  text-align: center;
}

/* 헤드라인을 세리프로 (이미지 느낌) */

.landing-title {
  font-family: 'Playfair Display', serif;
  letter-spacing: -0.5px;
}

/* 모바일에서 버튼 줄바꿈 시 간격 유지 */
@media (max-width: 576px) {
  .landing .btn { width: 100%; }
}
</style>
