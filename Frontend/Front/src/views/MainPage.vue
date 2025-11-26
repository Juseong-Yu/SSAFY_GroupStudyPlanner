<!-- src/views/MainPage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 main-page-wrapper d-flex flex-column">
        <!-- 상단 헤더 -->
        <div class="d-flex align-items-center justify-content-between mb-3 w-100">
          <div>
            <h2 class="fw-bold mb-0">내 일정</h2>
            <div class="small text-muted">
              개인 일정과 참여 중인 스터디 일정이 한 곳에 표시됩니다.
            </div>
          </div>

          <div class="d-flex gap-2">
            <button
              type="button"
              class="btn btn-outline-primary btn-sm"
              @click="openCreateModal"
            >
              + 개인 일정 추가
            </button>
          </div>
        </div>

        <!-- 캘린더 카드 -->
        <div class="card shadow-sm">
          <div
            class="card-body p-3"
            style="height: calc(100vh - 220px); display:flex; flex-direction:column;"
          >
            <div
              v-if="isLoading && !isMounted"
              class="py-5 text-center text-muted small"
            >
              불러오는 중...
            </div>
            <div v-else-if="isMounted" class="calendar-wrapper" style="flex:1;">
              <FullCalendar :options="calendarOptions" />
            </div>
          </div>
        </div>

        <!-- 도움말 -->
        <div class="mt-3 small text-muted">
          • 파란색: 스터디 일정 / 보라색: 개인 일정
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
            <!-- 제목만 -->
            <h5 class="mb-1 fw-bold">
              {{ detail?.data.schedule.title || '일정 상세' }}
            </h5>

            <!-- 오른쪽: 타입 배지 + 닫기 버튼 -->
            <div class="d-flex align-items-center gap-2 ms-auto">
              <span
                v-if="detail"
                class="badge rounded-pill small"
                :class="detail.type === 'study'
                  ? 'bg-primary-subtle text-primary'
                  : 'bg-purple-subtle text-purple'"
              >
                {{ detail.type === 'study' ? '스터디 일정' : '개인 일정' }}
              </span>
              <button
                type="button"
                class="btn btn-light btn-sm"
                @click="closeDetailModal"
              >
                닫기
              </button>
            </div>
          </div>

          <div class="card-body">
            <div v-if="detailError" class="alert alert-danger py-2 small mb-3">
              {{ detailError }}
            </div>

            <div
              v-if="!detail && !detailError"
              class="py-4 text-center text-muted small"
            >
              일정을 불러오는 중입니다...
            </div>

            <template v-else-if="detail">
              <!-- 왼쪽 정보 / 오른쪽 시간 요약 (SchedulePage와 비슷한 레이아웃) -->
              <div class="row g-4 align-items-start">
                <!-- 왼쪽: 정보 영역 -->
            <div class="col-12 col-md-7">

              <!-- 작성자 + hr (스터디 일정일 때만 전체 표시) -->
              <template v-if="detail.type === 'study' && detail.data.author">
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
                    {{ detail.data.author.username.charAt(0).toUpperCase() }}
                  </div>

                  <div class="small">
                    <div class="fw-semibold">
                      {{ detail.data.author.username }}
                    </div>
                    <div class="text-muted">
                      {{ detail.data.author.email }}
                    </div>
                  </div>
                </div>

                <hr class="my-3" />
              </template>

              <!-- 이 아래부터는 개인/스터디 공통 -->
              <div class="mb-4">
                <div class="fw-semibold small text-muted mb-1">일정 제목</div>
                <div class="fs-6">{{ detail.data.schedule.title }}</div>
              </div>

              <div class="mb-0">
                <div class="fw-semibold small text-muted mb-1">일정 상세</div>
                <p class="mb-0 small text-body" style="white-space: pre-wrap">
                  {{ detail.data.schedule.description || '내용 없음' }}
                </p>
              </div>

            </div>


                <!-- 오른쪽: 시간 요약 박스 -->
                <div class="col-12 col-md-5">
                  <div class="time-summary p-3 rounded-3 border small">
                    <div class="fw-semibold mb-3 d-flex align-items-center gap-2">
                      <span>시간 요약</span>
                    </div>

                    <div class="mb-3">
                      <div class="text-muted fw-semibold mb-1">시작</div>
                      <div>{{ formatShortDateUtc(detail.data.schedule.start_at) }}</div>
                      <div>{{ formatTimeUtc(detail.data.schedule.start_at) }}</div>
                    </div>

                    <div>
                      <div class="text-muted fw-semibold mb-1">종료</div>
                      <div>
                        {{
                          formatShortDateUtc(
                            detail.data.schedule.end_at || detail.data.schedule.start_at
                          )
                        }}
                      </div>
                      <div>
                        {{
                          formatTimeUtc(
                            detail.data.schedule.end_at || detail.data.schedule.start_at
                          )
                        }}
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

    <!-- ====================== -->
    <!-- 생성 모달 -->
    <!-- ====================== -->
    <div v-if="showCreateModal" class="schedule-modal-backdrop">
      <div class="schedule-modal">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0 fw-bold">일정 추가</h5>
          </div>

          <div class="card-body">
            <div
              v-if="errorMessage"
              class="alert alert-danger py-2 small"
            >
              {{ errorMessage }}
            </div>

            <form @submit.prevent="onSubmitCreate">
              <div class="mb-3">
                <label class="form-label fw-semibold">일정 제목</label>
                <input
                  v-model="form.title"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-4">
                <label class="form-label fw-semibold">일정 상세</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>

              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">시작 일시</label>
                  <div class="d-flex gap-2">
                    <input
                      v-model="form.startDate"
                      type="date"
                      class="form-control"
                      required
                    />
                    <input
                      v-model="form.startTime"
                      type="time"
                      class="form-control"
                    />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">종료 일시</label>
                  <div class="d-flex gap-2">
                    <input
                      v-model="form.endDate"
                      type="date"
                      class="form-control"
                      required
                    />
                    <input
                      v-model="form.endTime"
                      type="time"
                      class="form-control"
                    />
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  @click="closeCreateModal"
                >
                  취소
                </button>
                <button
                  type="submit"
                  class="btn btn-primary btn-sm"
                  :disabled="isSubmitting"
                >
                  {{ isSubmitting ? '저장 중...' : '저장' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { CalendarOptions } from '@fullcalendar/core'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

/* 타입 정의 */
interface CombinedScheduleCore {
  title: string
  description: string
  start_at: string
  end_at?: string | null
}

interface CombinedAuthor {
  id: number
  username: string
  email: string
  profile_img: string | null
}

interface CombinedStudy {
  id: number
  name: string
}

interface CombinedData {
  id: number
  schedule: CombinedScheduleCore
  author?: CombinedAuthor
  study?: CombinedStudy
  [key: string]: any
}

type ScheduleType = 'study' | 'personal'

interface StoredEvent {
  type: ScheduleType
  data: CombinedData
}

/* 상태 */
const isLoading = ref(false)
const isMounted = ref(false)

const showCreateModal = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  title: '',
  description: '',
  startDate: '',
  startTime: '',
  endDate: '',
  endTime: '',
})

const showDetailModal = ref(false)
const detailError = ref('')
const detail = ref<StoredEvent | null>(null)

const eventsMap = new Map<string, StoredEvent>()

/* FullCalendar 옵션 */
const calendarOptions = ref<CalendarOptions>({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  height: '100%',
  expandRows: true,
  locale: 'ko',
  selectable: true,
  timeZone: 'UTC',
  events: [],
  // 달력 클릭으로 일정 추가 안 함
  dateClick: () => {},
  eventClick: (info: any) => {
    const key = info.event.id as string
    const stored = eventsMap.get(key) || null
    if (!stored) {
      detailError.value = '일정 정보를 찾지 못했습니다.'
      detail.value = null
      showDetailModal.value = true
      return
    }
    detailError.value = ''
    detail.value = stored
    showDetailModal.value = true
  },
})

/* 날짜 유틸 */
const parseUtc = (value: string): Date => {
  if (!value) return new Date(NaN)
  return new Date(value)
}

const formatTimeUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ''
  const h = String(d.getUTCHours()).padStart(2, '0')
  const m = String(d.getUTCMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

const formatShortDateUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ''
  const month = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  return `${month}월 ${day}일`
}

/* 문자열 → datetime */
const buildDateTime = (date: string, time: string, fallback: string): string => {
  const d = (date || '').trim()
  if (!d) return ''
  const t = (time || '').trim() || fallback
  return `${d} ${t}`
}

/* 일정 로드 */
const loadSchedules = async () => {
  try {
    isLoading.value = true
    eventsMap.clear()
    detailError.value = ''

    const allRes = await axios.get<Array<{ type: ScheduleType; data: CombinedData }>>(
      `${API_BASE}/schedules/schedule_list/`,
      {
        withCredentials: true,
      },
    )
    const allData = allRes.data || []

    const events: any[] = []

    allData.forEach((item) => {
      const type: ScheduleType = item.type || 'personal'
      const data = item.data
      const key = `${type}-${data.id}`

      eventsMap.set(key, { type, data })

      const start = new Date(data.schedule.start_at)
      const end = new Date(data.schedule.end_at || data.schedule.start_at)

      if (
        end.getUTCHours() === 0 &&
        end.getUTCMinutes() === 0 &&
        end.getUTCSeconds() === 0 &&
        end.getUTCMilliseconds() === 0
      ) {
        end.setTime(end.getTime() - 1)
      }

      const isStudy = type === 'study'

      events.push({
        id: key,
        title: data.schedule.title,
        start,
        end,
        backgroundColor: isStudy ? '#e6f0ff' : '#f3e8ff',
        borderColor: isStudy ? '#bcd7ff' : '#d6bbff',
        textColor: '#0b1220',
      })
    })

    calendarOptions.value.events = events
  } catch (e) {
    console.error(e)
    detailError.value = '일정을 불러오는 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
  }
}

/* 상세 모달 */
const closeDetailModal = () => {
  showDetailModal.value = false
  detail.value = null
  detailError.value = ''
}

/* 생성 모달 */
const openCreateModal = () => {
  form.value = {
    title: '',
    description: '',
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
  }
  errorMessage.value = ''
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

/* 폼 검증 */
const validateForm = (): boolean => {
  const startStr = buildDateTime(form.value.startDate, form.value.startTime, '00:00')
  const endStr = buildDateTime(form.value.endDate, form.value.endTime, '23:59')

  if (!startStr || !endStr) {
    errorMessage.value = '날짜를 입력해주세요.'
    return false
  }

  const start = new Date(startStr)
  const end = new Date(endStr)

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    errorMessage.value = '날짜/시간 형식이 올바르지 않습니다.'
    return false
  }

  if (end < start) {
    errorMessage.value = '종료 시간이 더 빠릅니다.'
    return false
  }

  errorMessage.value = ''
  return true
}

/* 개인 일정 생성 */
const onSubmitCreate = async () => {
  if (!validateForm()) return

  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const start_at = buildDateTime(form.value.startDate, form.value.startTime, '00:00')
    const end_at = buildDateTime(form.value.endDate, form.value.endTime, '23:59')

    await axios.post(
      `${API_BASE}/schedules/personal_schedule_create/`,
      {
        title: form.value.title.trim(),
        description: form.value.description.trim(),
        start_at,
        end_at,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
          'Content-Type': 'application/json',
        },
      },
    )

    await loadSchedules()
    closeCreateModal()
  } catch (e) {
    console.error(e)
    errorMessage.value = '일정 생성에 실패했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

/* 작성자 아바타 (스터디 일정에서만 사용) */
const detailAuthorAvatar = computed(() => {
  const d = detail.value
  const author = d?.data.author
  if (!author || !author.profile_img) return null
  return `${API_BASE}${author.profile_img}`
})

/* 마운트 */
onMounted(async () => {
  isMounted.value = true
  await ensureCsrf()
  await loadSchedules()
})
</script>

<style scoped>
.main-page-wrapper {
  max-width: 1000px;
}

.calendar-wrapper :deep(.fc) {
  height: 100%;
  background-color: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0.5rem;
}

/* FullCalendar 스타일 */
:deep(.fc-toolbar-title) {
  color: #2b3a67;
  font-weight: 700;
}

:deep(.fc .fc-daygrid-day-number) {
  color: #212529;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-day-number:hover),
:deep(.fc .fc-daygrid-day-number:focus) {
  color: #212529;
}

:deep(.fc a) {
  color: inherit;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-event) {
  color: #212529;
}

:deep(.fc .fc-col-header-cell-cushion) {
  color: #3b4b70;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-day:hover) {
  background: #fafcff;
}

/* 캘린더 스크롤 */
.calendar-wrapper {
  overflow: auto;
}

:deep(.fc .fc-scroller) {
  overflow: auto !important;
  max-height: 100%;
}

/* 모달 스타일 (SchedulePage와 동일) */
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

.schedule-modal .card-header .btn {
  white-space: nowrap;
  padding-inline: 0.9rem;
}

.schedule-modal h5 {
  font-size: 1.1rem;
}

/* 시간 요약 박스 */
.time-summary {
  background: #f7f9fc;
}

/* 개인 일정 배지 색상 */
.bg-purple-subtle {
  background-color: #f3e8ff;
}

.text-purple {
  color: #6b21a8;
}
</style>
