<!-- src/views/StudyPage.vue -->
<template>
  <AppShell>
    <!-- ✅ 양쪽 여백 맞추기: 전체를 한 번 더 감싸서 max-width + 중앙 정렬 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <!-- ⬇⬇ 여기만 수정: inline style 제거 + study-page-wrapper 클래스 추가 -->
      <div class="w-100 study-page-wrapper">
        <h2 class="fw-bold mb-1">{{ studyTitle }}</h2>
        <p class="text-muted mb-4 small">
          참여 코드 : {{ studyId }}
        </p>

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
              <!-- ✅ 공지사항 -->
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
                  <!-- 🔥 최근 3개만 / 클릭 시 상세 페이지로 이동 -->
                  <RouterLink
                    v-for="n in topNotices"
                    :key="n.id"
                    :to="`/studies/${studyId}/notice/${n.id}`"
                    class="list-group-item py-3 text-reset text-decoration-none notice-link"
                  >
                    <div class="fw-semibold text-truncate mb-1">
                      {{ n.title }}
                    </div>

                    <div class="d-flex align-items-center text-muted small">
                      <!-- 아바타 -->
                      <img
                        v-if="n.author.profileImg"
                        :src="n.author.profileImg"
                        alt="avatar"
                        class="avatar me-2"
                        referrerpolicy="no-referrer"
                      />
                      <div v-else class="avatar avatar-fallback me-2">
                        {{ initials(n.author.username) }}
                      </div>

                      <!-- 작성자 이름 + 날짜 -->
                      <span class="me-2">{{ n.author.username }}</span>
                      <span aria-hidden="true" class="mx-1">·</span>
                      <time :datetime="n.createdAt">{{ formatDate(n.createdAt) }}</time>
                    </div>
                  </RouterLink>

                  <!-- 공지 없을 때 -->
                  <div
                    v-if="!topNotices.length && isLoaded"
                    class="list-group-item py-4 text-center text-muted small"
                  >
                    아직 등록된 공지사항이 없어요.
                  </div>
                </div>
              </div>

              <!-- ✅ 일정 카드 -->
              <div class="card shadow-sm">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <span class="fw-semibold">일정</span>
                  <RouterLink
                    :to="{ name: 'ScheduleMain', params: { id: studyId } }"
                    class="btn btn-sm btn-outline-primary"
                  >
                    전체보기
                  </RouterLink>
                </div>

                <div class="list-group list-group-flush">
                  <div
                    class="list-group-item py-3 list-item-clickable"
                    v-for="s in upcomingSchedules"
                    :key="s.id"
                    @click="openDetailModal(s.id)"
                  >
                    <div class="fw-semibold text-truncate">
                      {{ s.schedule.title }}
                    </div>
                    <div class="text-muted small">
                      {{ formatScheduleRange(s.schedule.start_at, s.schedule.end_at) }}
                    </div>
                  </div>

                  <div
                    v-if="!upcomingSchedules.length && isLoaded"
                    class="list-group-item py-4 text-center text-muted small"
                  >
                    아직 등록된 일정이 없어요.
                  </div>
                </div>
              </div>
            </div>
            <!-- /right-stack -->
          </div>
        </div>
      </div>
    </div>

    <!-- ====================== -->
    <!-- 일정 상세 모달 -->
    <!-- ====================== -->
    <div v-if="showDetailModal" class="schedule-modal-backdrop">
      <div class="schedule-modal">
        <div class="card shadow-sm">
          <div
            class="card-header d-flex justify-content-between align-items-start flex-wrap gap-2"
          >
            <div>
              <h5 class="mb-1 fw-bold">
                {{ detail?.schedule.title || '일정 상세' }}
              </h5>
            </div>
            <button
              type="button"
              class="btn btn-light btn-sm ms-auto"
              @click="closeDetailModal"
            >
              닫기
            </button>
          </div>

          <div class="card-body">
            <div v-if="detailError" class="alert alert-danger py-2 small mb-3">
              {{ detailError }}
            </div>
            <div v-if="isDetailLoading" class="py-4 text-center text-muted small">
              불러오는 중...
            </div>

            <template v-else-if="detail">
              <div class="row g-4 align-items-start">
                <!-- 왼쪽: 정보 -->
                <div class="col-12 col-md-7">
                  <div class="d-flex align-items-center mb-3">
                    <div
                      v-if="detailAuthorAvatar"
                      class="rounded-circle border bg-light me-3 overflow-hidden"
                      style="width: 44px; height: 44px"
                    >
                      <img
                        :src="detailAuthorAvatar"
                        alt="author"
                        class="w-100 h-100"
                        style="object-fit: cover"
                      />
                    </div>
                    <div
                      v-else
                      class="rounded-circle border bg-light me-3 d-flex align-items-center justify-content-center"
                      style="width: 44px; height: 44px; font-size: 0.8rem"
                    >
                      {{ detail.author.username.charAt(0).toUpperCase() }}
                    </div>
                    <div class="small">
                      <div class="fw-semibold">{{ detail.author.username }}</div>
                      <div class="text-muted">{{ detail.author.email }}</div>
                    </div>
                  </div>

                  <hr class="my-3" />

                  <div class="mb-4">
                    <div class="fw-semibold small text-muted mb-1">일정 제목</div>
                    <div class="fs-6">{{ detail.schedule.title }}</div>
                  </div>

                  <div class="mb-0">
                    <div class="fw-semibold small text-muted mb-1">일정 상세</div>
                    <p class="mb-0 small text-body" style="white-space: pre-wrap">
                      {{ detail.schedule.description || '내용 없음' }}
                    </p>
                  </div>
                </div>

                <!-- 오른쪽: 시간 요약 -->
                <div class="col-12 col-md-5">
                  <div class="time-summary p-3 rounded-3 border small">
                    <div class="fw-semibold mb-3 d-flex align-items-center gap-2">
                      <span>시간 요약</span>
                    </div>

                    <div class="mb-3">
                      <div class="text-muted fw-semibold mb-1">시작</div>
                      <div>{{ formatDateOnly(detail.schedule.start_at) }}</div>
                      <div>{{ formatTimeOnly(detail.schedule.start_at) }}</div>
                    </div>

                    <div>
                      <div class="text-muted fw-semibold mb-1">종료</div>
                      <div>
                        {{ formatDateOnly(detail.schedule.end_at || detail.schedule.start_at) }}
                      </div>
                      <div>
                        {{ formatTimeOnly(detail.schedule.end_at || detail.schedule.start_at) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

/** FullCalendar */
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { CalendarOptions } from '@fullcalendar/core'

// 백엔드 베이스 URL
const API_BASE = import.meta.env.VITE_API_BASE_URL as string

const route = useRoute()

// 🔗 스터디 기본 정보
const studyId = computed(() => Number(route.params.id))
const studyTitle = ref('스터디 불러오는 중...')
const studyLeader = ref<string | null>(null)
const joinedAt = ref<string | null>(null)
const createdAt = ref<string | null>(null)

const isMounted = ref(false)
const isLoaded = ref(false) // 공지 / 스터디 / 일정 로딩 여부

onMounted(() => {
  isMounted.value = true
})

/* =========================
 *   공지사항 타입 / 상태
 * ========================= */

// 백엔드 응답 그대로
interface ApiNotice {
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

// 프론트에서 쓰기 편한 형태
type Notice = {
  id: number
  title: string
  createdAt: string
  author: {
    id: number
    username: string
    email: string
    profileImg: string | null
  }
}

// 전체 공지 목록 (원본)
const notices = ref<Notice[]>([])

// 앞 페이지에 보여줄 최근 3개 공지
const topNotices = computed(() =>
  [...notices.value]
    .sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )
    .slice(0, 3)
)

/* =========================
 *   일정 타입 / 상태
 * ========================= */

interface StudyScheduleItem {
  id: number
  schedule: {
    id: number
    title: string
    description: string
    start_at: string // "2025-11-21T13:00:00Z"
    end_at: string   // "2025-11-22T00:00:00Z"
  }
  author: {
    id: number
    username: string
    email: string
    profile_img: string | null
  }
  study: {
    id: number
    name: string
  }
}

const schedules = ref<StudyScheduleItem[]>([])

/* 상세 조회 타입 / 상태 */

interface ScheduleAuthor {
  id: number
  username: string
  email: string
  profile_img: string | null
}

interface ScheduleStudy {
  id: number
  name: string
}

interface ScheduleDetail {
  id: number
  schedule: {
    title: string
    description: string
    start_at: string
    end_at: string | null
  }
  author: ScheduleAuthor
  study: ScheduleStudy
}

const showDetailModal = ref(false)
const isDetailLoading = ref(false)
const detailError = ref('')
const detail = ref<ScheduleDetail | null>(null)

/* =========================
 *   API 호출 함수들
 * ========================= */

// 🔗 스터디 조회 API 호출
async function fetchStudy() {
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const { data } = await axios.get(`${API_BASE}/studies/${studyId.value}/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
      },
    })

    studyTitle.value = data.name ?? '이름 없는 스터디'
    studyLeader.value = data.leader ?? null
    joinedAt.value = data.joined_at ?? null
    createdAt.value = data.created_at ?? null
  } catch (error) {
    console.error('스터디 조회 실패:', error)
    studyTitle.value = '스터디 정보를 불러오지 못했어요'
  }
}

// 🔗 일정 목록 조회 API 호출
async function fetchSchedules() {
  try {
    await ensureCsrf()

    const { data } = await axios.get<StudyScheduleItem[]>(
      `${API_BASE}/studies/${studyId.value}/schedules/study_schedule_list/`,
      {
        withCredentials: true,
      }
    )

    schedules.value = data

    const fcEvents = data.map((item) => {
      const start = new Date(item.schedule.start_at)
      const end = new Date(item.schedule.end_at)

      // ✅ end가 정확히 자정이면 1ms 빼서 "전날 23:59:59.999"로 맞추기
      if (
        end.getHours() === 0 &&
        end.getMinutes() === 0 &&
        end.getSeconds() === 0 &&
        end.getMilliseconds() === 0
      ) {
        end.setTime(end.getTime() - 1)
      }

      return {
        id: String(item.id), // 🔥 detail에서 사용하는 id와 맞추기
        title: item.schedule.title,
        start,
        end,
        backgroundColor: '#e7f1ff', // 아주 연한 파랑
        borderColor: '#b6d4fe',     // 보통 파랑
        textColor: '#084298',
      }
    })

    calendarOptions.value.events = fcEvents
  } catch (error) {
    console.error('일정 목록 조회 실패:', error)
    schedules.value = []
    calendarOptions.value.events = []
  }
}

// 🔗 공지사항 목록 조회 API 호출
async function fetchNotices() {
  try {
    await ensureCsrf()

    const { data } = await axios.get<ApiNotice[]>(
      `${API_BASE}/studies/${studyId.value}/posts/notice_list/`,
      {
        withCredentials: true,
      }
    )

    notices.value = data.map((n) => ({
      id: n.id,
      title: n.title,
      createdAt: n.created_at,
      author: {
        id: n.author.id,
        username: n.author.username,
        email: n.author.email,
        // 🔥 여기서 절대경로로 변환
        profileImg: n.author.profile_img
          ? `${API_BASE}${n.author.profile_img}`
          : null,
      },
    }))
  } catch (error) {
    console.error('공지사항 목록 조회 실패:', error)
    notices.value = []
  }
}

/* =========================
 *   유틸 함수들
 * ========================= */

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

// 일정 기간 표시 (MM/DD HH:mm ~ ...)
function formatScheduleRange(startIso: string, endIso: string) {
  const start = new Date(startIso)
  const end = new Date(endIso)

  const startDate = `${start.getMonth() + 1}/${start.getDate()}`
  const startTime = `${String(start.getHours()).padStart(2, '0')}:${String(
    start.getMinutes()
  ).padStart(2, '0')}`

  const endDate = `${end.getMonth() + 1}/${end.getDate()}`
  const endTime = `${String(end.getHours()).padStart(2, '0')}:${String(
    end.getMinutes()
  ).padStart(2, '0')}`

  if (startDate === endDate) {
    return `${startDate} ${startTime} ~ ${endTime}`
  }
  return `${startDate} ${startTime} ~ ${endDate} ${endTime}`
}

// 모달 시간용 (로컬 날짜/시간)
function formatDateOnly(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}

function formatTimeOnly(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mi}`
}

/* =========================
 *   오른쪽 카드 계산 값
 * ========================= */

// ✅ 오늘 00:00 기준(과거 일정 필터용)
const today = new Date()
today.setHours(0, 0, 0, 0)

// 오른쪽 카드에 보여줄 상위 3개 일정 (과거 일정 제외)
const upcomingSchedules = computed(() =>
  schedules.value
    // 이미 끝난 일정(end_at < 오늘 00:00)은 제외
    .filter((item) => {
      const end = new Date(item.schedule.end_at)
      return end.getTime() >= today.getTime()
    })
    // 가까운 일정 순으로 정렬
    .sort(
      (a, b) =>
        new Date(a.schedule.start_at).getTime() -
        new Date(b.schedule.start_at).getTime()
    )
    // 상위 3개만 노출
    .slice(0, 3)
)

/* =========================
 *   FullCalendar 옵션
 * ========================= */

const calendarOptions = ref<CalendarOptions>({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  height: 'auto',
  locale: 'ko',
  selectable: true,
  timeZone: 'UTC', // 서버에서 오는 ISO(UTC)를 그대로 쓰기
  events: [],
  dateClick: (info: any) => {
    console.log('dateClick:', info.dateStr)
  },
})

/* =========================
 *   일정 상세 모달 관련
 * ========================= */

async function openDetailModal(id: number) {
  if (!studyId.value) return
  showDetailModal.value = true
  isDetailLoading.value = true
  detailError.value = ''
  detail.value = null

  try {
    await ensureCsrf()
    const { data } = await axios.get<ScheduleDetail>(
      `${API_BASE}/studies/${studyId.value}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
      }
    )
    detail.value = data
  } catch (e) {
    console.error(e)
    detailError.value = '일정 정보를 불러오지 못했습니다.'
  } finally {
    isDetailLoading.value = false
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  detail.value = null
  detailError.value = ''
}

/* author 아바타 */
const detailAuthorAvatar = computed(() => {
  if (!detail.value || !detail.value.author.profile_img) return null
  return `${API_BASE}${detail.value.author.profile_img}`
})

/* =========================
 *   스터디 ID 변경 감시
 * ========================= */

watch(
  studyId,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return
    isLoaded.value = false

    try {
      await fetchStudy()
      await fetchSchedules()
      await fetchNotices()
    } finally {
      isLoaded.value = true
    }
  },
  { immediate: true }
)

// 캘린더 이벤트 클릭 → 상세 모달
watch(
  () => calendarOptions.value.events,
  () => {
    calendarOptions.value.eventClick = (info: any) => {
      const id = Number(info.event.id)
      if (!Number.isNaN(id)) {
        openDetailModal(id)
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
/* ✅ 반응형 메인 래퍼: 화면 넓어질수록 조금씩 더 넓게 */
.study-page-wrapper {
  max-width: 1000px; /* 기본값: 기존과 비슷 */
}

@media (min-width: 992px) {
  .study-page-wrapper {
    max-width: 1140px;
  }
}

@media (min-width: 1200px) {
  .study-page-wrapper {
    max-width: 1320px;
  }
}

@media (min-width: 1400px) {
  .study-page-wrapper {
    max-width: 1440px;
  }
}

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

/* 요일 헤더(월화수목금토일) 색상 */
:deep(.fc .fc-col-header-cell-cushion) {
  color: #3b4b70;
  text-decoration: none;
}
:deep(.fc .fc-col-header-cell-cushion:hover),
:deep(.fc .fc-col-header-cell-cushion:focus) {
  color: #3b4b70;
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

/* 공지 카드 클릭 스타일 */
.notice-link:hover {
  background-color: #f8fafc;
}

/* 일정 리스트 hover 느낌 */
.list-item-clickable {
  cursor: pointer;
}
.list-item-clickable:hover {
  background-color: #f8fafc;
}

/* 모달 공통 */
.schedule-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.schedule-modal {
  width: 100%;
  max-width: 760px;
  padding: 0 1rem;
}

.schedule-modal .card {
  border-radius: 18px;
  border: none;
}

.schedule-modal .card-header {
  padding: 1.25rem 1.75rem 1rem;
}

.schedule-modal .card-body {
  padding: 1.5rem 1.75rem 1.75rem;
}

/* 시간 요약 박스 */
.time-summary {
  background: #f7f9fc;
}
</style>
