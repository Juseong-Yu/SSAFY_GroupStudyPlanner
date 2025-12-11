<!-- src/views/MainPage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 main-page-wrapper d-flex flex-column">
        <!-- 상단 헤더 -->
        <div class="d-flex align-items-center justify-content-between mb-3 w-100">
          <div>
            <h2 class="fw-bold mb-0">내 일정</h2>
            <div class="small text-muted mt-1">
              개인 일정과 참여 중인 스터디 일정이 한 곳에 표시됩니다.
            </div>
          </div>

          <div class="d-flex gap-2">
            <button
              type="button"
              class="btn btn-light-outline btn-sm"
              @click="openCreateModal"
            >
              + 개인 일정 추가
            </button>
          </div>
        </div>

        <!-- ✅ BaseScheduleCalendar 사용 -->
        <BaseScheduleCalendar
          :events="calendarEvents"
          :loading="isLoading && !isMounted"
          @event-click="handleEventClick"
        >
          <template #footer>
            <div class="mt-3 small text-muted">
              • 파란색: 스터디 일정 / 보라색: 개인 일정
            </div>
          </template>
        </BaseScheduleCalendar>
      </div>
    </div>

    <!-- ====================== -->
    <!-- ✅ 공용 일정 상세 모달 (스터디/개인 공통 디자인) -->
    <!-- ====================== -->
    <ScheduleDetailModal
      :show="showDetailModal"
      :error="detailError"
      :detail="detail"
      user-role="member"              
      @close="closeDetailModal"
      @delete="handleDeleteSchedule"
      @edit="handleEditSchedule"
    />

    <!-- ====================== -->
    <!-- 생성 / 수정 모달 -->
    <!-- ====================== -->
    <div v-if="showCreateModal" class="schedule-modal-backdrop">
      <div class="schedule-modal">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0 fw-bold">
              {{ isEditing ? '일정 수정' : '일정 추가' }}
            </h5>
          </div>

          <div class="card-body">
            <div v-if="errorMessage" class="alert alert-danger py-2 small">
              {{ errorMessage }}
            </div>

            <form @submit.prevent="onSubmitCreate">
              <div class="mb-3">
                <label class="form-label fw-semibold">일정 제목</label>
                <input v-model="form.title" type="text" class="form-control" required />
              </div>

              <div class="mb-4">
                <label class="form-label fw-semibold">일정 상세</label>
                <textarea v-model="form.description" class="form-control" rows="3"></textarea>
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
                    <input v-model="form.startTime" type="time" class="form-control" />
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
                    <input v-model="form.endTime" type="time" class="form-control" />
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
                <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">
                  {{ isSubmitting ? '저장 중...' : isEditing ? '수정' : '저장' }}
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
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import BaseScheduleCalendar from '@/components/BaseScheduleCalendar.vue'
import type { EventInput, EventClickArg } from '@fullcalendar/core'
import ScheduleDetailModal, {
  type StoredEvent,
} from '@/components/ScheduleDetailModal.vue'

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

const isEditing = ref(false)
const editingId = ref<number | null>(null)

/* BaseScheduleCalendar 에 내려줄 이벤트 배열 */
const calendarEvents = ref<EventInput[]>([])

/* 이벤트 원본 저장용 (상세 모달에서 사용) */
const eventsMap = new Map<string, StoredEvent>()

/* 문자열 → datetime */
const buildDateTime = (date: string, time: string, fallback: string): string => {
  const d = (date || '').trim()
  if (!d) return ''
  const t = (time || '').trim() || fallback
  return `${d} ${t}`
}

/* 일정 로드 (개인 + 스터디) */
const loadSchedules = async () => {
  try {
    isLoading.value = true
    eventsMap.clear()
    detailError.value = ''

    const allRes = await client.get<Array<{ type: ScheduleType; data: CombinedData }>>(
      `${API_BASE}/schedules/schedule_list/`,
      {
        withCredentials: true,
      },
    )
    const allData = allRes.data || []

    const events: EventInput[] = []

    allData.forEach((item) => {
      const type: ScheduleType = item.type || 'personal'
      const data = item.data
      const key = `${type}-${data.id}`

      eventsMap.set(key, { type, data })

      const start = new Date(data.schedule.start_at)
      const end = new Date(data.schedule.end_at || data.schedule.start_at)

      // 종일 처리: 00:00 으로 들어오는 경우 -1ms 해서 하루 안에만 보이게
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
        backgroundColor: isStudy ? '#e4edff' : '#f5ecff',
        borderColor: isStudy ? '#a7c4ff' : '#ceb5ff',
        textColor: '#111827',
      })
    })

    calendarEvents.value = events
  } catch (e) {
    console.error(e)
    detailError.value = '일정을 불러오는 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
  }
}

/* BaseScheduleCalendar 의 event-click 핸들러 */
const handleEventClick = (info: EventClickArg) => {
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
}

/* 상세 모달 닫기 */
const closeDetailModal = () => {
  showDetailModal.value = false
  detail.value = null
  detailError.value = ''
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

/* 생성 모달 열기 (새 개인 일정) */
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
  isEditing.value = false
  editingId.value = null
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

/* 개인 일정 생성 / 수정 */
const onSubmitCreate = async () => {
  if (!validateForm()) return

  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const start_at = buildDateTime(form.value.startDate, form.value.startTime, '00:00')
    const end_at = buildDateTime(form.value.endDate, form.value.endTime, '23:59')

    const payload = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      start_at,
      end_at,
    }

    if (isEditing.value && editingId.value !== null) {
      // ✅ 개인 일정 수정
      await client.put(
        `${API_BASE}/schedules/${editingId.value}/personal_schedule_detail/`,
        payload,
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': csrftoken || '',
            'Content-Type': 'application/json',
          },
        },
      )
    } else {
      // ✅ 개인 일정 생성
      await client.post(`${API_BASE}/schedules/personal_schedule_create/`, payload, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
          'Content-Type': 'application/json',
        },
      })
    }

    await loadSchedules()
    closeCreateModal()
  } catch (e) {
    console.error(e)
    errorMessage.value = isEditing.value
      ? '일정 수정에 실패했습니다.'
      : '일정 생성에 실패했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

/* 개인 일정 수정 트리거 (모달에서 edit emit) */
const handleEditSchedule = (payload: StoredEvent) => {
  // ✅ 개인 일정만 허용
  if (payload.type !== 'personal') return

  const data = payload.data
  const start = new Date(data.schedule.start_at)
  const end = new Date(data.schedule.end_at || data.schedule.start_at)

  const toDateStr = (d: Date) => d.toISOString().slice(0, 10) // YYYY-MM-DD
  const toTimeStr = (d: Date) =>
    `${String(d.getHours()).padStart(2, '0')}:${String(
      d.getMinutes(),
    ).padStart(2, '0')}`

  form.value = {
    title: data.schedule.title,
    description: data.schedule.description || '',
    startDate: toDateStr(start),
    startTime: toTimeStr(start),
    endDate: toDateStr(end),
    endTime: toTimeStr(end),
  }

  isEditing.value = true
  editingId.value = data.id

  showDetailModal.value = false
  showCreateModal.value = true
}

/* 개인 일정 삭제 */
const handleDeleteSchedule = async (id: number) => {
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.delete(`${API_BASE}/schedules/${id}/personal_schedule_detail/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken || '',
      },
    })

    await loadSchedules()
    closeDetailModal()
  } catch (e) {
    console.error(e)
    detailError.value = '일정 삭제에 실패했습니다.'
  }
}

/* 마운트 */
onMounted(async () => {
  isMounted.value = true
  await ensureCsrf()
  await loadSchedules()
})
</script>

<style scoped>
.main-page-wrapper {
  width: 100%;
  max-width: 1300px;
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 768px) {
  .main-page-wrapper {
    max-width: 1300px;
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

/* 모달 스타일 (생성 모달용) */
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

/* 개인 일정 배지 색상 (ScheduleDetailModal에서 재사용 가능) */
.bg-purple-subtle {
  background-color: #f3e8ff;
}
.text-purple {
  color: #6b21a8;
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
</style>
