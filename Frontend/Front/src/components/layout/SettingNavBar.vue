<!-- src/components/layout/SettingNavBar.vue -->
<template>
  <div class="sidebar d-flex flex-column vh-100 bg-light shadow-sm position-relative">
    <!-- 헤더 -->
    <div class="d-flex align-items-center justify-content-between p-3 border-bottom">
      <div class="fw-semibold">설정</div>
    </div>

    <!-- 메뉴 -->
    <div class="menu-section flex-grow-1 mt-3">
      <ul class="list-unstyled mb-0">
        <li class="mb-2">
          <RouterLink
            to="/settings/profile"
            class="nav-item-link d-flex align-items-center px-3 py-2 text-decoration-none text-dark"
          >
            <i class="bi bi-person-circle me-2"></i>
            프로필
          </RouterLink>
        </li>
        <li>
          <!-- 비밀번호 확인을 거쳐 설정 페이지로 라우팅하는 기존 플로우 유지 -->
          <RouterLink
            to="/accounts/password-check"
            class="nav-item-link d-flex align-items-center px-3 py-2 text-decoration-none text-dark"
          >
            <i class="bi bi-gear me-2"></i>
            설정
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 이 컴포넌트는 라우팅만 하므로 별도 로직 없음
</script>

<style scoped>
.sidebar {
  width: 250px; /* 기존 사이드바와 동일 크기 */
}

/* hover 효과 및 활성 라우트 스타일 */
.nav-item-link {
  border-radius: 8px;
}
.nav-item-link:hover {
  background-color: #f8f9fa;
}

/* RouterLink 활성화 색상 (기존과 동일한 느낌) */
.router-link-active {
  font-weight: 600;
  color: #0d6efd !important;
}
</style>
