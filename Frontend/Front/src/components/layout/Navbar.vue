<template>
  <!-- 오버레이 (모바일 전용) -->
  <div
    v-if="ui.sidebarOpen"
    class="sidebar-backdrop d-lg-none"
    @click="ui.closeSidebar"
  ></div>

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
        <!-- 프로필 이미지: 로딩/미설정 대비 -->
        <template v-if="user.loading">
          <span class="placeholder rounded-circle me-2" style="width: 30px; height: 30px"></span>
          <div class="placeholder col-4" style="height: 1rem"></div>
        </template>
        <template v-else>
          <!-- 이미지 있으면 <img>, 없거나 깨지면 bi-person-fill -->
          <div
            class="rounded-circle border d-inline-flex justify-content-center align-items-center bg-light me-2"
            style="width: 30px; height: 30px"
          >
            <template v-if="hasAvatar && !avatarBroken">
              <img
                :src="avatarSrc"
                alt="Profile"
                class="rounded-circle"
                width="30"
                height="30"
                style="object-fit: cover"
                @error="onAvatarError"
              />
            </template>
            <template v-else>
              <i class="bi bi-person-fill text-secondary" aria-hidden="true"></i>
            </template>
          </div>

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
          <!-- 모달 오픈용 항목 -->
          <li>
            <button
              class="dropdown-item"
              type="button"
              data-bs-toggle="modal"
              data-bs-target="#createStudyModal"
              @click="(closeMenu(), maybeCloseOnMobile())"
            >
              스터디 생성
            </button>
          </li>
          <li>
            <button
              class="dropdown-item"
              type="button"
              data-bs-toggle="modal"
              data-bs-target="#joinStudyModal"
              @click="(closeMenu(), maybeCloseOnMobile())"
            >
              스터디 참여
            </button>
          </li>

          <li><hr class="dropdown-divider" /></li>

          <li>
            <RouterLink to="/settings/profile" class="dropdown-item" @click="closeMenu">
              설정
            </RouterLink>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li>
            <!-- 로그아웃 -->
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
        <!-- 관리(리더) -->
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
            <!-- 로딩 -->
            <li v-if="studies.loading" class="mt-1">
              <div class="placeholder-glow">
                <span class="placeholder col-9"></span>
              </div>
              <div class="placeholder-glow mt-1">
                <span class="placeholder col-7"></span>
              </div>
            </li>
            <!-- 오류 -->
            <li v-else-if="studies.error" class="text-danger mt-1">
              {{ studies.error }}
            </li>
            <!-- 빈 상태 -->
            <li v-else-if="studies.leaderCount === 0" class="text-muted mt-1">
              생성한 스터디가 없습니다.
            </li>
            <!-- 목록 -->
            <li v-else v-for="s in studies.leader" :key="`leader-${s.id}`" class="mt-1">
              <RouterLink
                :to="`/studies/${s.id}`"
                class="d-flex align-items-center justify-content-between text-decoration-none text-dark"
                :class="{ 'text-muted': s.is_active === false }"
                :title="`리더: ${s.leader ?? ''} · 생성일: ${s.created_at ?? ''}`"
                @click="maybeCloseOnMobile"
              >
                <span class="text-truncate">{{ s.name }}</span>
              </RouterLink>
            </li>
          </ul>
        </li>

        <!-- 참여(멤버) -->
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
            <!-- 로딩 -->
            <li v-if="studies.loading" class="mt-1">
              <div class="placeholder-glow">
                <span class="placeholder col-8"></span>
              </div>
              <div class="placeholder-glow mt-1">
                <span class="placeholder col-6"></span>
              </div>
            </li>
            <!-- 오류 -->
            <li v-else-if="studies.error" class="text-danger mt-1">
              {{ studies.error }}
            </li>
            <!-- 빈 상태 -->
            <li v-else-if="studies.memberCount === 0" class="text-muted mt-1">
              참여 중인 스터디가 없습니다.
            </li>
            <!-- 목록 -->
            <li v-else v-for="s in studies.member" :key="`member-${s.id}`" class="mt-1">
              <RouterLink
                :to="`/studies/${s.id}`"
                class="d-flex align-items-center justify-content-between text-decoration-none text-dark"
                :class="{ 'text-muted': s.is_active === false }"
                :title="`리더: ${s.leader ?? ''} · 참여일: ${s.joined_at ?? ''}`"
                @click="maybeCloseOnMobile"
              >
                <span class="text-truncate">{{ s.name }}</span>
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </aside>

  <!-- 스터디 생성 모달 (이름만 입력) -->
  <div
    class="modal fade"
    id="createStudyModal"
    tabindex="-1"
    aria-labelledby="createStudyLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <form class="modal-content" @submit.prevent="submitCreate">
        <div class="modal-header">
          <h5 class="modal-title" id="createStudyLabel">스터디 생성</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="닫기"
          ></button>
        </div>

        <div class="modal-body">
          <div v-if="create.error" class="alert alert-danger py-2">{{ create.error }}</div>

          <div class="mb-1">
            <label class="form-label">스터디 이름</label>
            <input
              v-model.trim="create.form.title"
              class="form-control"
              placeholder="예) 알고리즘 스터디"
            />
          </div>
          <small class="text-muted">필수: 스터디 이름만 설정합니다.</small>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-outline-secondary"
            data-bs-dismiss="modal"
            :disabled="create.loading"
          >
            취소
          </button>
          <button type="submit" class="btn btn-primary" :disabled="create.loading">
            <span
              v-if="create.loading"
              class="spinner-border spinner-border-sm me-2"
              role="status"
            ></span>
            생성
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- 스터디 참여 모달 -->
  <div
    class="modal fade"
    id="joinStudyModal"
    tabindex="-1"
    aria-labelledby="joinStudyLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <form class="modal-content" @submit.prevent="submitJoin">
        <div class="modal-header">
          <h5 class="modal-title" id="joinStudyLabel">스터디 참여</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="닫기"
          ></button>
        </div>

        <div class="modal-body">
          <div v-if="join.error" class="alert alert-danger py-2">{{ join.error }}</div>

          <div class="mb-3">
            <label class="form-label">참여 코드</label>
            <input v-model.trim="join.code" class="form-control" placeholder="예) ABCD-1234" />
            <div class="form-text">리더가 공유한 참여 코드를 입력하세요.</div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-outline-secondary"
            data-bs-dismiss="modal"
            :disabled="join.loading"
          >
            닫기
          </button>
          <button type="submit" class="btn btn-primary" :disabled="join.loading || !join.code">
            <span
              v-if="join.loading"
              class="spinner-border spinner-border-sm me-2"
              role="status"
            ></span>
            참여하기
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { useStudiesStore } from '@/stores/studies'
import { resetAllStores } from '@/stores/resetAllStores'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

const ui = useUiStore()
const user = useUserStore()
const studies = useStudiesStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

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
  if (!ui.isLgUp) ui.closeSidebar()
}

/** 프로필 표시용 계산 (닉네임 그대로) */
const usernameDisplay = computed(() => user.profile?.nickname ?? '로그인 필요')

/** 아바타 폴백 최소 로직 */
const avatarBroken = ref(false)
const hasAvatar = computed(() => !!user.profile?.avatar_url)
const avatarSrc = computed(() => user.profile?.avatar_url || '')
const onAvatarError = () => {
  avatarBroken.value = true
}

/** 로그아웃: 스토어 액션 호출 + 모든 store reset */
const handleLogoutClick = async () => {
  closeMenu()
  maybeCloseOnMobile()

  try {
    await user.logout()
    resetAllStores()
  } catch (e) {
    console.error(e)
  }
}

/* ============================
   스터디 생성/참여 로직
   ============================ */

const create = ref({
  loading: false,
  error: '',
  form: { title: '' },
})
function resetCreate() {
  create.value.loading = false
  create.value.error = ''
  create.value.form = { title: '' }
}

const join = ref({ loading: false, error: '', code: '' })
function resetJoin() {
  join.value.loading = false
  join.value.error = ''
  join.value.code = ''
}

function hideBsModalById(id: string) {
  const el = document.getElementById(id)
  if (!el) return

  // 1) bootstrap.bundle 이 있는 경우
  // @ts-ignore
  const bs = (window as any)?.bootstrap
  if (bs?.Modal) {
    try {
      const inst = bs.Modal.getInstance(el) || new bs.Modal(el)
      inst.hide()
      return
    } catch {}
  }

  // 2) 폴백
  el.classList.remove('show')
  el.setAttribute('aria-hidden', 'true')
  el.removeAttribute('aria-modal')
  el.style.display = 'none'
  document.body.classList.remove('modal-open')
  document.body.style.removeProperty('padding-right')
  document.body.style.removeProperty('overflow')
  const backdrops = document.querySelectorAll('.modal-backdrop')
  backdrops.forEach((b) => b.parentElement?.removeChild(b))
}

const submitCreate = async () => {
  if (!create.value.form.title.trim()) {
    create.value.error = '스터디 이름을 입력하세요.'
    return
  }

  try {
    create.value.loading = true
    create.value.error = ''

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const payload = {
      name: create.value.form.title.trim(),
    }

    await axios.post(`${API_BASE}/studies/study/`, payload, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
    })

    await studies.refresh()

    hideBsModalById('createStudyModal')
    resetCreate()
  } catch (e: any) {
    console.error(e)
    create.value.error =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      '스터디 생성 중 오류가 발생했습니다.'
  } finally {
    create.value.loading = false
  }
}

const submitJoin = async () => {
  if (!join.value.code.trim() || join.value.loading) return

  try {
    join.value.loading = true
    join.value.error = ''

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const payload = {
      id: join.value.code.trim(),
    }

    await axios.post(`${API_BASE}/studies/join/`, payload, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
    })

    await studies.refresh()

    hideBsModalById('joinStudyModal')
    resetJoin()
  } catch (e: any) {
    console.error(e)
    join.value.error =
      e?.response?.data?.detail || e?.response?.data?.message || '참여 코드가 올바르지 않습니다.'
  } finally {
    join.value.loading = false
  }
}

onMounted(() => {
  user.loadIfNeeded()
  studies.loadIfNeeded()

  document.addEventListener('click', onClickOutside, { capture: true })
  document.addEventListener('keydown', onEscape)

  document.documentElement.style.setProperty('--sidebar-width', '250px')
  document.documentElement.style.setProperty('--gap', '20px')
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, { capture: true })
  document.removeEventListener('keydown', onEscape)
})
</script>

<style scoped>
/* 사이드바: 기본 닫힘 (슬라이드) */
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

/* 오버레이 (모바일 전용: d-lg-none로 제어) */
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

/* 긴 목록 대비 내부 스크롤 */
.menu-section {
  overflow: auto;
}

/* 모달 백드롭/모달 z-index를 올려 네비게이션 바까지 어둡게 덮기 (scoped → :deep) */
:deep(.modal-backdrop) {
  z-index: 5000 !important; /* 네비게이션 바 z-index보다 충분히 크게 */
}
:deep(.modal) {
  z-index: 5005 !important;
}

/* 항목 hover */
:deep(a.text-dark):hover {
  text-decoration: underline;
}
</style>
