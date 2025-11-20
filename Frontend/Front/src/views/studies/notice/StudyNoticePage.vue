<!-- src/views/StudyNoticePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex flex-column align-items-center">
      <!-- 제목 -->
      <div
        class="d-flex align-items-center justify-content-between mb-4 w-100"
        style="max-width: 950px"
      >
        <h2 class="fw-bold mb-0">내가 만든 스터디 &gt; 공지사항</h2>
        <RouterLink :to="`/studies/${studyId}/create`" class="btn btn-outline-primary">
          +add
        </RouterLink>
      </div>

      <!-- 카드 -->
      <div class="card shadow-sm w-100 notice-card" style="max-width: 950px">
        <div class="card-body p-0">
          <div class="table-responsive mb-0">
            <table class="table align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Title</th>
                  <th class="text-end" style="width: 320px">작성자</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="row in pagedNotices" :key="row.id">
                  <!-- 제목 셀 (왼쪽 마진 추가) -->
                  <td class="py-3 title-cell">
                    <div class="fw-semibold text-truncate">Text line</div>
                  </td>

                  <td class="py-3 text-end">
                    <div class="d-inline-flex align-items-center gap-2 justify-content-end">
                      <img
                        v-if="row.author.avatarUrl"
                        :src="row.author.avatarUrl"
                        alt="avatar"
                        class="avatar"
                        referrerpolicy="no-referrer"
                      />
                      <div v-else class="avatar avatar-fallback">
                        {{ initials(row.author.name) }}
                      </div>
                      <div class="text-end">
                        <div class="small fw-semibold">{{ row.author.name }}</div>
                        <div class="small text-muted">{{ formatDate(row.createdAt) }}</div>
                      </div>
                    </div>
                  </td>
                </tr>

                <tr v-if="!pagedNotices.length">
                  <td colspan="2" class="text-center text-muted py-5">공지사항이 없습니다.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div
        class="d-flex flex-column flex-sm-row align-items-center justify-content-between gap-2 mt-3 w-100"
        style="max-width: 950px"
      >
        <div class="text-muted small">
          Page {{ currentPage }} / {{ totalPages }} · Total {{ total }} items
        </div>

        <nav aria-label="pagination">
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="goPrev" :disabled="currentPage === 1">Prev</button>
            </li>

            <li
              v-for="p in pageWindow"
              :key="p"
              class="page-item"
              :class="{ active: p === currentPage }"
            >
              <button class="page-link" @click="goPage(p)">{{ p }}</button>
            </li>

            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="goNext" :disabled="currentPage === totalPages">
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

type Row = {
  id: number
  createdAt: string
  author: { name: string; avatarUrl?: string }
}

// 임시 데이터
const total = 92
const pageSize = ref(10)
const currentPage = ref(1)

const route = useRoute()
const studyId = route.params.id

const allRows = computed<Row[]>(() =>
  Array.from({ length: total }, (_, i) => ({
    id: i + 1,
    createdAt: '2025-10-' + String((i % 28) + 1).padStart(2, '0') + 'T09:00:00Z',
    author:
      i % 3 === 0
        ? { name: '주성 유' }
        : i % 3 === 1
          ? { name: '홍길동', avatarUrl: 'https://i.pravatar.cc/64?img=12' }
          : { name: '김코치', avatarUrl: 'https://i.pravatar.cc/64?img=32' },
  })),
)

const totalPages = computed(() => Math.max(1, Math.ceil(total / pageSize.value)))

const pagedNotices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return allRows.value.slice(start, start + pageSize.value)
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

function initials(name: string) {
  const [a = '', b = ''] = name.trim().split(/\s+/, 2)
  return ((a[0] || '') + (b[0] || '')).toUpperCase()
}

function formatDate(iso: string) {
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}
</script>

<style scoped>
/* 카드 테두리 문제 해결 */
.notice-card {
  overflow: hidden;
  border-radius: 0.75rem;
  border: 1px solid #dee2e6;
}

.notice-card .table {
  margin-bottom: 0;
}

/* 제목 왼쪽 마진 */
.title-cell {
  padding-left: 12px;
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
</style>
