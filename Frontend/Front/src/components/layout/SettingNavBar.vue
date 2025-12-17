<template>
  <div class="sidebar d-flex flex-column vh-100 bg-light shadow-sm position-relative">
    <!-- 헤더 -->
    <div class="d-flex align-items-center justify-content-between p-3 border-bottom">
      <div class="fw-semibold">설정</div>

      <!-- ✅ 메인 페이지로 이동 아이콘 버튼 -->
      <RouterLink
        to="/main"
        class="btn btn-sm p-0 border-0 bg-transparent text-secondary home-btn"
        title="메인으로"
      >
        <i class="bi bi-house-door fs-5"></i>
      </RouterLink>
    </div>

    <!-- 메뉴 -->
    <div class="menu-section grow mt-3">
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
          <RouterLink
            to="/settings/connect"
            class="nav-item-link d-flex align-items-center px-3 py-2 text-decoration-none text-dark"
          >
            <i class="bi bi-plug-fill me-2"></i>
            외부 서비스 연동
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 라우팅 전용, 별도 로직 없음
</script>

<style scoped>
.sidebar {
  width: 250px;
}

/* hover 효과 및 활성 라우트 스타일 */
.nav-item-link {
  border-radius: 8px;
}
.nav-item-link:hover {
  background-color: #f8f9fa;
}

/* RouterLink 활성화 색상 */
.router-link-active {
  font-weight: 600;
  color: #495057;
}


/* ✅ 오른쪽 상단 홈 버튼 */
.home-btn {
  color: #6c757d;
  transition: color 0.2s;
}
.home-btn:hover {
  color: #0d6efd;
}
</style>
