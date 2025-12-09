<!-- src/views/StudyNoticePage.vue -->
<template>
  <AppShell>
    <!-- 스터디/일정 페이지와 동일한 레이아웃 패턴 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper d-flex flex-column">
        <!-- 제목 영역 -->
        <div class="d-flex align-items-center justify-content-between mb-4 w-100">
          <h2 class="fw-bold mb-0">공지사항</h2>
          <RouterLink v-if="canManageNotices" :to="`/studies/${studyId}/notice/create`"
            class="btn btn-light-outline btn-sm">
            + 공지 생성
          </RouterLink>

        </div>

        <!-- 공지 목록 카드 -->
        <div class="card shadow-sm w-100 notice-card">
          <div class="card-body p-0">
            <div class="table-responsive mb-0">
              <table class="table align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Title</th>
                    <th class="text-end pe-4" style="width: 260px">작성자</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="row in pagedNotices" :key="row.id">
                    <!-- 제목 셀 (왼쪽 마진 + 디테일 페이지 링크) -->
                    <td class="py-3 title-cell">
                      <RouterLink :to="{
                        name: 'NoticeDetail',
                        params: { id: studyId, noticeId: row.id },
                      }" class="fw-semibold text-truncate title-link">
                        {{ row.title }}
                      </RouterLink>
                    </td>

                    <td class="py-3 text-end">
                      <div class="d-inline-flex align-items-center gap-2 justify-content-end me-3">
                        <img v-if="row.author.avatarUrl" :src="row.author.avatarUrl" alt="avatar" class="avatar"
                          referrerpolicy="no-referrer" />
                        <div v-else class="avatar avatar-fallback">
                          <i class="bi bi-person-fill text-secondary" aria-hidden="true"></i>
                        </div>
                        <div class="text-end">
                          <div class="small fw-semibold">
                            {{ row.author.name }}
                          </div>
                          <div class="small text-muted">
                            {{ formatDate(row.createdAt) }}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>

                  <tr v-if="!pagedNotices.length">
                    <td colspan="2" class="text-center text-muted py-5">
                      공지사항이 없습니다.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 0"
          class="pagination-wrapper d-flex flex-column flex-md-row align-items-center justify-content-between gap-2 mt-3 w-100">
          <div class="text-muted small">
            총 <span class="fw-semibold">{{ total }}</span>개 ·
            <span class="fw-semibold">{{ currentPage }}</span> / {{ totalPages }} 페이지
          </div>

          <nav aria-label="공지 페이지 이동">
            <ul class="pagination pagination-sm mb-0">
              <!-- Prev -->
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link icon-btn" @click="goPrev" :disabled="currentPage === 1">
                  <i class="bi bi-chevron-left" aria-hidden="true"></i>
                </button>
              </li>

              <!-- 페이지 번호 -->
              <li v-for="p in pageWindow" :key="p" class="page-item" :class="{ active: p === currentPage }">
                <button class="page-link" @click="goPage(p)">
                  {{ p }}
                </button>
              </li>

              <!-- Next -->
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link icon-btn" @click="goNext" :disabled="currentPage === totalPages">
                  <i class="bi bi-chevron-right" aria-hidden="true"></i>
                </button>
              </li>
            </ul>
          </nav>
        </div>

      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'
import { useStudyRoleStore } from '@/stores/studyRoleStore'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// 백엔드 응답 타입
type NoticeFromAPI = {
  id: number
  title: string
  created_at: string
  updated_at: string
  study_id: number
  author: {
    id: number
    username: string
    email: string
    profile_img: string | null
  }
}

// 화면에서 쓰는 Row 타입
type Row = {
  id: number
  title: string
  createdAt: string
  author: {
    name: string
    avatarUrl?: string | null
  }
}

const route = useRoute()
const studyId = route.params.id as string

const studyRoleStore = useStudyRoleStore()

// 공지 생성 권한 (leader 또는 admin)
const canManageNotices = computed(() => studyRoleStore.isAdmin(studyId))

// 실제 공지 데이터
const notices = ref<Row[]>([])

// 페이지네이션 상태
const pageSize = ref(10)
const currentPage = ref(1)

// 총 개수는 응답 길이로 계산
const total = computed(() => notices.value.length)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / pageSize.value)),
)

const pagedNotices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return notices.value.slice(start, start + pageSize.value)
})

const pageWindow = computed(() => {
  const span = 5
  const half = Math.floor(span / 2)
  let start = Math.max(1, currentPage.value - half)
  let end = start + span - 1
  if (end > totalPages.value) {
    end = totalPages.value
    start = Math.max(1, end - span + 1)
  }
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

function goPrev() {
  if (currentPage.value > 1) currentPage.value--
}
function goNext() {
  if (currentPage.value < totalPages.value) currentPage.value++
}
function goPage(p: number) {
  if (p >= 1 && p <= totalPages.value) currentPage.value = p
}

// 이니셜
function initials(name: string) {
  const [a = '', b = ''] = name.trim().split(/\s+/, 2)
  return ((a[0] || '') + (b[0] || '')).toUpperCase()
}

// 날짜 포맷
function formatDate(iso: string) {
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}

// 공지 목록 불러오기
onMounted(async () => {
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const res = await axios.get<NoticeFromAPI[]>(
      `${API_BASE}/studies/${studyId}/posts/notice_list/`,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken ?? '',
        },
      },
    )

    notices.value = res.data.map((n) => ({
      id: n.id,
      title: n.title,
      createdAt: n.created_at,
      author: {
        name: n.author.username,
        avatarUrl: n.author.profile_img
          ? `${API_BASE}${n.author.profile_img}`
          : null,
      },
    }))
  } catch (error) {
    console.error('공지 목록 불러오기 실패:', error)
  }
})
</script>

<style scoped>
/* StudyPage / SchedulePage와 공통으로 쓰는 반응형 너비 */
.study-page-wrapper {
  width: 100%;
  max-width: 1300px;
  padding-left: 0.5rem;
  /* 항상 좌우 여백 유지 */
  padding-right: 0.5rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 768px) {
  .study-page-wrapper {
    max-width: 1300px;
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

/* 카드 테두리 문제 해결 */
.notice-card {
  overflow: hidden;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.notice-card .table {
  margin-bottom: 0;
}

/* 제목 왼쪽 마진 */
.title-cell {
  padding-left: 24px;
}

/* 제목 링크 스타일 */
.title-link {
  display: block;
  color: inherit;
  text-decoration: none;
}

.title-link:hover {
  text-decoration: underline;
}

/* avatar styles */
.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-fallback {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  background: #e9eef7;
  color: #2b3a67;
}

.table thead th {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  padding-left: 24px;
  padding-right: 12px;
}

/* 버튼 스타일 */
.btn-light-outline {
  border: 1px solid #d0d7e2;
  background-color: #ffffff;
  color: #475569;
  border-radius: 8px;
  transition: 0.2s ease;
}

.btn-light-outline:hover {
  background-color: #f1f5f9;
  border-color: #c5cedb;
}

/* 페이지네이션 pill 느낌으로 커스텀 */
.pagination .page-link {
  border-radius: 6px !important;
  border: none;
  background: transparent;
  color: #475569;
  padding-inline: 0.6rem;
}

.pagination .page-link:hover {
  background: #f1f5f9;
}

.pagination .page-item.active .page-link {
  background: #e2e8f0;
  color: #0f172a;
  font-weight: 600;
}
</style>
