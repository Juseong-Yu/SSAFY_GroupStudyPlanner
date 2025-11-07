<!-- src/views/MainPage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4">
      <h2 class="fw-bold mb-1">{{ studyTitle }}</h2>
      <p class="text-muted mb-4 small">code : {{ studyId }}</p>

      <div class="row g-4">
        <!-- 왼쪽: 달력 -->
        <div class="col-12 col-xl-8">
          <div v-if="isMounted" class="calendar-wrapper">
            <FullCalendar :options="calendarOptions" />
          </div>
        </div>

        <!-- 오른쪽: 공지사항 + 일정 -->
        <div class="col-12 col-xl-4">
          <div class="right-stack sticky-xl-top" style="top: 88px">
            <!-- ✅ 공지사항 (체크박스/버튼 제거 + 작성자 아바타/이름/날짜) -->
            <div class="card mb-3 shadow-sm">
              <div class="card-header d-flex align-items-center justify-content-between">
                <span class="fw-semibold">공지사항</span>
                <RouterLink
                  :to="{ name: 'NoticeMain', params: { id: studyId } }"
                  class="btn btn-sm btn-outline-primary"
                >
                  전체보기
                </RouterLink>
              </div>

              <div class="list-group list-group-flush">
                <div v-for="n in notices" :key="n.id" class="list-group-item py-3" role="button">
                  <div class="fw-semibold text-truncate mb-1">{{ n.title }}</div>

                  <div class="d-flex align-items-center text-muted small">
                    <!-- 아바타 -->
                    <img
                      v-if="n.author.avatarUrl"
                      :src="n.author.avatarUrl"
                      alt="avatar"
                      class="avatar me-2"
                      referrerpolicy="no-referrer"
                    />
                    <div v-else class="avatar avatar-fallback me-2">
                      {{ initials(n.author.name) }}
                    </div>

                    <!-- 작성자 이름 + 날짜 -->
                    <span class="me-2">{{ n.author.name }}</span>
                    <span aria-hidden="true" class="mx-1">·</span>
                    <time :datetime="n.createdAt">{{ formatDate(n.createdAt) }}</time>
                  </div>
                </div>
              </div>
            </div>

            <!-- 일정 (그대로 목업, 다음 단계에서 작업) -->
            <div class="card shadow-sm">
              <div class="card-header d-flex align-items-center justify-content-between">
                <span class="fw-semibold">일정</span>
                <a href="#" class="btn btn-sm btn-outline-primary">전체보기</a>
              </div>
              <div class="list-group list-group-flush">
                <div class="list-group-item py-3" v-for="n in 3" :key="'sch-' + n">
                  <div class="fw-semibold">Title</div>
                  <div class="text-muted small">Text line</div>
                </div>
              </div>
            </div>
          </div>
          <!-- /right-stack -->
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'

/** FullCalendar */
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'

const route = useRoute()
const studyId = computed(() => Number(route.params.id))
const studyTitle = computed(() => '내가 만든 스터디') // 백엔드 붙으면 교체

const isMounted = ref(false)
onMounted(() => {
  isMounted.value = true
})

// ---- 공지사항 목업 데이터 (API 붙이면 여기만 교체) ----
type Notice = {
  id: number
  title: string
  createdAt: string // ISO
  author: { name: string; avatarUrl?: string }
}
const notices = ref<Notice[]>([
  {
    id: 1,
    title: '이번 주 알고리즘 과제 공지',
    createdAt: '2025-10-21T09:12:00Z',
    author: { name: '주성 유', avatarUrl: '' },
  },
  {
    id: 2,
    title: '10/27 스터디 정기 모임 장소 변경',
    createdAt: '2025-10-20T14:03:00Z',
    author: { name: '홍길동', avatarUrl: 'https://i.pravatar.cc/64?img=12' },
  },
  {
    id: 3,
    title: '중간시험 대비 자료 업로드 안내',
    createdAt: '2025-10-18T02:10:00Z',
    author: { name: '김코치', avatarUrl: 'https://i.pravatar.cc/64?img=32' },
  },
])

// 이니셜 생성
function initials(name: string) {
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] ?? ''
  const last = parts[1]?.[0] ?? ''
  return (first + last).toUpperCase()
}

// 날짜 표시 (yyyy.mm.dd)
function formatDate(iso: string) {
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}

// ---- 캘린더 옵션(변경 없음) ----
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  height: 'auto',
  locale: 'ko',
  selectable: true,
  events: [
    { title: '스터디 회의', start: '2025-10-24' },
    { title: '알고리즘 과제 마감', start: '2025-10-27' },
  ],
  dateClick: (info: any) => {
    console.log('dateClick:', info.dateStr)
  },
})
</script>

<style scoped>
/* 캘린더 카드 느낌 */
.calendar-wrapper :deep(.fc) {
  background-color: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1rem;
}
:deep(.fc-toolbar-title) {
  color: #2b3a67;
  font-weight: 700;
}
:deep(.fc-col-header-cell) {
  background: #f7f9fc;
  font-weight: 600;
  color: #3b4b70;
}
:deep(.fc .fc-daygrid-day-number),
:deep(.fc .fc-daygrid-day-number:link),
:deep(.fc .fc-daygrid-day-number:visited),
:deep(.fc .fc-daygrid-day-number:hover),
:deep(.fc .fc-daygrid-day-number:focus),
:deep(.fc .fc-daygrid-day-number:active) {
  color: inherit !important;
  text-decoration: none !important;
  cursor: default !important;
  outline: none !important;
}
:deep(.fc .fc-daygrid-day:hover) {
  background: #fafcff;
}
:deep(.fc .fc-daygrid-event a) {
  color: inherit;
  text-decoration: none;
}

/* 공지사항 아바타 */
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

.right-stack .card {
  border-radius: 1rem;
}
</style>
