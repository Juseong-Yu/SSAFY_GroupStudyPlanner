<!-- src/views/studies/SchedulePage.vue -->
<template>
  <AppShell>
    <!-- StudyPage와 동일한 너비 전략: 가운데 정렬 + 반응형 max-width -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper d-flex flex-column">
        <!-- 상단 헤더 -->
        <div class="d-flex align-items-center justify-content-between mb-2 w-100">
          <div>
            <h2 class="fw-bold mb-0">스터디 일정</h2>
          </div>

          <!-- 일정 추가 버튼 -->
          <button
    v-if="canManageSchedules"
    type="button"
    class="btn btn-light-outline btn-sm"
    @click="openCreateModal"
  >
    + 일정 추가
  </button>
        </div>

        <!-- 상태 요약 배지 -->
        <div class="w-100 mb-4">
          <div class="d-flex flex-wrap gap-2 small">
            <span class="badge rounded-pill bg-primary-subtle text-primary">
              진행중 {{ ongoingSchedules.length }}개
            </span>
            <span class="badge rounded-pill bg-success-subtle text-success">
              다가오는 {{ upcomingSchedules.length }}개
            </span>
            <span class="badge rounded-pill bg-secondary-subtle text-secondary">
              지난 일정 {{ pastSchedules.length }}개
            </span>
          </div>
        </div>

        <!-- 뷰 전환 토글 (캘린더 / 목록) - 노션 스타일, 왼쪽 정렬 -->
        <div class="d-flex justify-content-start mb-3">
          <div class="schedule-view-toggle d-inline-flex align-items-center">
            <button type="button" class="toggle-btn" :class="{ 'is-active': viewMode === 'calendar' }"
              @click="viewMode = 'calendar'">
              캘린더
            </button>
            <button type="button" class="toggle-btn" :class="{ 'is-active': viewMode === 'list' }"
              @click="viewMode = 'list'">
              목록
            </button>
          </div>
        </div>

        <!-- 본문: 선택한 뷰만 보여주기 -->
        <div class="w-100 schedule-main">
          <!-- ✅ 캘린더 뷰: BaseScheduleCalendar 사용 -->
          <div v-if="viewMode === 'calendar'" class="schedule-main-calendar">
            <BaseScheduleCalendar :events="calendarEvents" :loading="isLoading" @event-click="handleEventClick" />
          </div>

          <!-- 목록(카드) 뷰 -->
          <div v-else>
            <!-- 진행중 일정 -->
            <div class="card shadow-sm mb-3" v-if="ongoingSchedules.length || isLoading">
              <div class="card-header d-flex align-items-center justify-content-between schedule-section-header-today">
                <span class="fw-semibold small">진행중인 일정</span>
                <span class="badge bg-primary-subtle text-primary small">
                  {{ ongoingSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div v-if="!ongoingSchedules.length && !isLoading" class="py-3 text-center text-muted small">
                  진행중인 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div v-for="item in ongoingSchedules" :key="'ongoing-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)">
                    <!-- 시작 날짜만 (시간 X) -->
                    <div class="schedule-time text-muted me-3">
                      <div class="fw-semibold small">
                        {{ formatShortDateUtc(item.schedule.start_at) }}
                      </div>
                    </div>

                    <div class="flex-grow-1">
                      <div class="d-flex align-items-start justify-content-between mb-1">
                        <div class="fw-semibold text-truncate me-2">
                          {{ item.schedule.title }}
                        </div>
                        <span class="badge rounded-pill bg-primary-subtle text-primary small">
                          진행중
                        </span>
                      </div>
                      <div class="text-muted small text-truncate mb-1">
                        {{ item.schedule.description }}
                      </div>
                      <div class="text-muted small">
                        {{ formatRangeUtc(item.schedule.start_at, item.schedule.end_at) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 다가오는 일정 -->
            <div class="card shadow-sm mb-3" v-if="upcomingSchedules.length || isLoading">
              <div class="card-header d-flex align-items-center justify-content-between">
                <span class="fw-semibold small">다가오는 일정</span>
                <span class="badge bg-success-subtle text-success small">
                  {{ upcomingSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div v-if="!upcomingSchedules.length && !isLoading" class="py-3 text-center text-muted small">
                  다가오는 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div v-for="item in upcomingSchedules" :key="'upcoming-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)">
                    <!-- 시작 날짜만 (시간 X) -->
                    <div class="schedule-time text-muted me-3">
                      <div class="fw-semibold small">
                        {{ formatShortDateUtc(item.schedule.start_at) }}
                      </div>
                    </div>

                    <div class="flex-grow-1">
                      <div class="d-flex align-items-start justify-content-between mb-1">
                        <div class="fw-semibold text-truncate me-2">
                          {{ item.schedule.title }}
                        </div>
                        <span v-if="getDDay(item) !== null"
                          class="badge rounded-pill bg-success-subtle text-success small">
                          {{ getDDay(item) === 0 ? "D-day" : "D-" + getDDay(item) }}
                        </span>
                      </div>
                      <div class="text-muted small text-truncate mb-1">
                        {{ item.schedule.description }}
                      </div>
                      <div class="text-muted small">
                        {{ formatRangeUtc(item.schedule.start_at, item.schedule.end_at) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 지난 일정 -->
            <div class="card shadow-sm" v-if="pastSchedules.length || isLoading">
              <div class="card-header d-flex align-items-center justify-content-between">
                <span class="fw-semibold small">지난 일정</span>
                <span class="badge bg-secondary-subtle text-secondary small">
                  {{ pastSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div v-if="!pastSchedules.length && !isLoading" class="py-3 text-center text-muted small">
                  지난 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div v-for="item in pastSchedules.slice(0, 5)" :key="'past-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)">
                    <!-- 시작 날짜만 (시간 X) -->
                    <div class="schedule-time text-muted me-3">
                      <div class="fw-semibold small">
                        {{ formatShortDateUtc(item.schedule.start_at) }}
                      </div>
                    </div>

                    <div class="flex-grow-1">
                      <div class="fw-semibold text-truncate mb-1">
                        {{ item.schedule.title }}
                      </div>
                      <div class="text-muted small text-truncate mb-1">
                        {{ item.schedule.description }}
                      </div>
                      <div class="text-muted small">
                        {{ formatRangeUtc(item.schedule.start_at, item.schedule.end_at) }}
                      </div>
                    </div>
                  </div>

                  <!-- 나중에 진짜 히스토리 페이지 만들면 RouterLink로 교체 -->
                  <div v-if="pastSchedules.length > 5" class="list-group-item text-center small text-muted">
                    지난 일정 더보기 ({{ pastSchedules.length - 5 }}개)
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- /viewMode === 'list' -->
        </div>
      </div>
    </div>

    <!-- ====================== -->
    <!-- 일정 상세 모달: ScheduleDetailModal 사용 -->
    <!-- ====================== -->
    <ScheduleDetailModal :show="showDetailModal" :error="detailError" :detail="detail" @close="closeDetailModal"
      @delete="handleDetailDelete" />

    <!-- ====================== -->
    <!-- 일정 추가 모달 (기존 그대로 사용) -->
    <!-- ====================== -->
    <div v-if="showCreateModal" class="schedule-modal-backdrop">
      <div class="schedule-modal">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0 fw-bold">일정 추가</h5>
          </div>

          <div class="card-body">
            <!-- 에러 메시지 -->
            <div v-if="errorMessage" class="alert alert-danger py-2 small">
              {{ errorMessage }}
            </div>

            <form @submit.prevent="onSubmitCreate">
              <!-- 제목 -->
              <div class="mb-3">
                <label class="form-label fw-semibold">일정 제목</label>
                <input v-model="form.title" type="text" class="form-control" required />
              </div>

              <!-- 상세 -->
              <div class="mb-4">
                <label class="form-label fw-semibold">일정 상세</label>
                <textarea v-model="form.description" class="form-control" rows="3"></textarea>
              </div>

              <!-- 시작 / 종료 -->
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">시작 일시</label>
                  <div class="d-flex gap-2">
                    <input v-model="form.startDate" type="date" class="form-control" required />
                    <input v-model="form.startTime" type="time" class="form-control" />
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">종료 일시</label>
                  <div class="d-flex gap-2">
                    <input v-model="form.endDate" type="date" class="form-control" required />
                    <input v-model="form.endTime" type="time" class="form-control" />
                  </div>
                </div>
              </div>

              <!-- 버튼 -->
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-outline-secondary btn-sm" @click="closeCreateModal">
                  취소
                </button>
                <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">
                  {{ isSubmitting ? "저장 중..." : "저장" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <!-- 모달 끝 -->
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import axios from "axios"
import AppShell from "@/layouts/AppShell.vue"
import { ensureCsrf, getCookie } from "@/utils/csrf_cors"

import BaseScheduleCalendar from "@/components/BaseScheduleCalendar.vue"
import ScheduleDetailModal, {
  type StoredEvent,
} from "@/components/ScheduleDetailModal.vue"
import { useStudyRoleStore } from "@/stores/studyRoleStore"   
import type { EventInput, EventClickArg } from "@fullcalendar/core"

/* ==============================
   라우트 / 상수
================================= */
const route = useRoute()
const studyId = route.params.id as string
const API_BASE = import.meta.env.VITE_API_BASE_URL || ""

/* ==============================
   뷰 전환 상태
================================= */
const viewMode = ref<"calendar" | "list">("calendar")

/* ==============================
   타입 정의
================================= */

interface ScheduleCore {
  id?: number
  title: string
  description: string
  start_at: string // ISO UTC
  end_at?: string | null
}

interface ScheduleItem {
  id: number
  schedule: ScheduleCore
}

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

interface ScheduleDetailResponse {
  id: number
  schedule: ScheduleCore
  author: ScheduleAuthor
  study: ScheduleStudy
}

/* ==============================
   상태
================================= */

const schedules = ref<ScheduleItem[]>([])
const isLoading = ref(false)

/* 생성 모달 상태 */
const showCreateModal = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref("")

const form = ref({
  title: "",
  description: "",
  startDate: "",
  startTime: "",
  endDate: "",
  endTime: "",
})

/* 상세 모달 상태 (ScheduleDetailModal용) */
const showDetailModal = ref(false)
const detailError = ref("")
const detail = ref<StoredEvent | null>(null)

/* ==============================
   FullCalendar 이벤트 데이터
================================= */

const calendarEvents = computed<EventInput[]>(() =>
  schedules.value.map((item) => {
    const start = new Date(item.schedule.start_at)
    const end = new Date(item.schedule.end_at || item.schedule.start_at)

    // end가 자정이면 하루 길게 잡히지 않도록 1ms 당기기
    if (
      end.getUTCHours() === 0 &&
      end.getUTCMinutes() === 0 &&
      end.getUTCSeconds() === 0 &&
      end.getUTCMilliseconds() === 0
    ) {
      end.setTime(end.getTime() - 1)
    }

    return {
      id: String(item.id),
      title: item.schedule.title,
      start,
      end,
      backgroundColor: "#e7f1ff",
      borderColor: "#b6d4fe",
      textColor: "#084298",
    }
  })
)

/* ==============================
   날짜 유틸 (UTC 기준)
================================= */

const parseUtc = (value: string): Date => {
  if (!value) return new Date(NaN)
  return new Date(value)
}

const formatTimeUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ""
  const h = String(d.getUTCHours()).padStart(2, "0")
  const m = String(d.getUTCMinutes()).padStart(2, "0")
  return `${h}:${m}`
}

const formatShortDateUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ""
  const month = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  return `${month}월 ${day}일`
}

const formatRangeUtc = (startIso: string, endIso?: string | null): string => {
  const s = parseUtc(startIso)
  const e = endIso ? parseUtc(endIso) : null

  if (isNaN(s.getTime())) return ""

  const sDate = `${s.getUTCMonth() + 1}월 ${s.getUTCDate()}일`
  const sTime = `${String(s.getUTCHours()).padStart(2, "0")}:${String(
    s.getUTCMinutes()
  ).padStart(2, "0")}`

  if (!e || isNaN(e.getTime()) || e <= s) {
    return `${sDate} ${sTime}`
  }

  const eDate = `${e.getUTCMonth() + 1}월 ${e.getUTCDate()}일`
  const eTime = `${String(e.getUTCHours()).padStart(2, "0")}:${String(
    e.getUTCMinutes()
  ).padStart(2, "0")}`

  if (
    s.getUTCFullYear() === e.getUTCFullYear() &&
    s.getUTCMonth() === e.getUTCMonth() &&
    s.getUTCDate() === e.getUTCDate()
  ) {
    return `${sDate} ${sTime} ~ ${eTime}`
  }
  return `${sDate} ${sTime} ~ ${eDate} ${eTime}`
}

/* D-day (다가오는 일정용) */
const getDDay = (item: ScheduleItem): number | null => {
  const now = new Date()
  const todayZero = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  ).getTime()

  const start = parseUtc(item.schedule.start_at)
  if (isNaN(start.getTime())) return null

  const startZero = new Date(
    start.getFullYear(),
    start.getMonth(),
    start.getDate()
  ).getTime()

  const diffDays = Math.round((startZero - todayZero) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return null
  return diffDays
}

/* ==============================
   진행중 / 다가오는 / 지난 일정
================================= */

const ongoingSchedules = computed<ScheduleItem[]>(() => {
  const now = Date.now()

  return schedules.value
    .filter((item) => {
      const s = parseUtc(item.schedule.start_at)
      const e = parseUtc(item.schedule.end_at || item.schedule.start_at)
      if (isNaN(s.getTime()) || isNaN(e.getTime())) return false
      return s.getTime() <= now && e.getTime() >= now
    })
    .sort(
      (a, b) =>
        parseUtc(a.schedule.start_at).getTime() -
        parseUtc(b.schedule.start_at).getTime()
    )
})

const upcomingSchedules = computed<ScheduleItem[]>(() => {
  const now = Date.now()

  return schedules.value
    .filter((item) => {
      const s = parseUtc(item.schedule.start_at)
      if (isNaN(s.getTime())) return false
      return s.getTime() > now
    })
    .sort(
      (a, b) =>
        parseUtc(a.schedule.start_at).getTime() -
        parseUtc(b.schedule.start_at).getTime()
    )
})

const pastSchedules = computed<ScheduleItem[]>(() => {
  const now = Date.now()

  return schedules.value
    .filter((item) => {
      const e = parseUtc(item.schedule.end_at || item.schedule.start_at)
      if (isNaN(e.getTime())) return false
      return e.getTime() < now
    })
    .sort(
      (a, b) =>
        parseUtc(b.schedule.end_at || b.schedule.start_at).getTime() -
        parseUtc(a.schedule.end_at || a.schedule.start_at).getTime()
    )
})

/* ==============================
   CRUD API
================================= */

const fetchSchedules = async () => {
  try {
    isLoading.value = true
    const res = await axios.get<ScheduleItem[]>(
      `${API_BASE}/studies/${studyId}/schedules/study_schedule_list/`,
      {
        withCredentials: true,
      }
    )
    schedules.value = res.data || []
  } finally {
    isLoading.value = false
  }
}

const onClickDelete = async (id: number) => {
  if (!confirm("삭제하시겠습니까?")) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie("csrftoken")

    await axios.delete(
      `${API_BASE}/studies/${studyId}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
        headers: { "X-CSRFToken": csrftoken || "" },
      }
    )

    schedules.value = schedules.value.filter((i) => i.id !== id)
    await fetchSchedules()
  } catch {
    alert("삭제에 실패했습니다.")
  }
}

/* ==============================
   상세 조회 (ScheduleDetailModal용 데이터로 변환)
================================= */

const openDetailModal = async (id: number) => {
  showDetailModal.value = true
  detailError.value = ""
  detail.value = null

  try {
    const res = await axios.get<ScheduleDetailResponse>(
      `${API_BASE}/studies/${studyId}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
      }
    )

    const stored: StoredEvent = {
      type: "study",
      data: {
        id: res.data.id,
        schedule: {
          title: res.data.schedule.title,
          description: res.data.schedule.description,
          start_at: res.data.schedule.start_at,
          end_at: res.data.schedule.end_at,
        },
        author: res.data.author,
        study: res.data.study,
      },
    }

    detail.value = stored
  } catch (e) {
    console.error(e)
    detailError.value = "일정 상세를 불러오지 못했습니다."
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  detail.value = null
  detailError.value = ""
}

/* BaseScheduleCalendar → event 클릭 */
const handleEventClick = (arg: EventClickArg) => {
  const id = Number(arg.event.id)
  if (!Number.isNaN(id)) {
    openDetailModal(id)
  }
}

/* ScheduleDetailModal에서 개인 일정 삭제 이벤트를 emit하지만,
   이 페이지는 study 일정만 사용하므로 실제로 호출될 일은 없음.
   그래도 타입 맞게 핸들러만 정의. */
const handleDetailDelete = async (id: number) => {
  await onClickDelete(id)
  closeDetailModal()
}

/* ==============================
   생성 관련
================================= */

const buildDateTime = (date: string, time: string, fallback: string): string => {
  const d = (date || "").trim()
  if (!d) return ""
  const t = (time || "").trim() || fallback
  return `${d} ${t}`
}

const openCreateModal = () => {
  form.value = {
    title: "",
    description: "",
    startDate: "",
    startTime: "",
    endDate: "",
    endTime: "",
  }
  errorMessage.value = ""
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

const validateForm = (): boolean => {
  const startStr = buildDateTime(form.value.startDate, form.value.startTime, "00:00")
  const endStr = buildDateTime(form.value.endDate, form.value.endTime, "23:59")

  if (!startStr || !endStr) {
    errorMessage.value = "날짜를 입력해주세요."
    return false
  }

  const start = new Date(startStr)
  const end = new Date(endStr)

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    errorMessage.value = "날짜/시간 형식이 올바르지 않습니다."
    return false
  }

  if (end < start) {
    errorMessage.value = "종료 시간이 더 빠릅니다."
    return false
  }

  errorMessage.value = ""
  return true
}

const onSubmitCreate = async () => {
  if (!validateForm()) return

  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie("csrftoken")

    const start_at = buildDateTime(
      form.value.startDate,
      form.value.startTime,
      "00:00"
    )
    const end_at = buildDateTime(
      form.value.endDate,
      form.value.endTime,
      "23:59"
    )

    await axios.post(
      `${API_BASE}/studies/${studyId}/schedules/study_schedule_create/`,
      {
        title: form.value.title.trim(),
        description: form.value.description.trim(),
        start_at,
        end_at,
      },
      {
        withCredentials: true,
        headers: {
          "X-CSRFToken": csrftoken || "",
          "Content-Type": "application/json",
        },
      }
    )

    await fetchSchedules()
    closeCreateModal()
  } finally {
    isSubmitting.value = false
  }
}

  /* ==============================
   권한
================================= */
const studyRoleStore = useStudyRoleStore()

// 이 스터디에서 일정 관리 권한 여부 (leader 또는 admin)
const canManageSchedules = computed(() =>
  studyRoleStore.isAdmin(studyId)
)

/* ==============================
   Mount
================================= */
onMounted(async () => {
  await ensureCsrf()
  await fetchSchedules()
})
</script>

<style scoped>
/* StudyPage와 동일한 반응형 너비 */
.study-page-wrapper {
  max-width: 1000px;
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

/* 본문 영역을 화면 기준으로 거의 꽉 채우기
   (AppShell 헤더/상단 여백 정도만 빼고) */
.schedule-main {
  height: calc(100vh - 220px);
  max-height: calc(100vh - 220px);
}

/* 캘린더 컨테이너 */
.schedule-main-calendar {
  height: 100%;
}

/* 카드 공통 */
.schedule-time {
  width: 90px;
  font-weight: 500;
  font-size: 0.8rem;
}

.schedule-section-header-today {
  background: #eef4ff;
  color: #1d4ed8;
}

/* 공통 모달 백드롭 (생성 모달용) */
.schedule-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

/* 모달 자체를 조금 더 키우고, 양옆 여백 추가 */
.schedule-modal {
  width: 100%;
  max-width: 760px;
  padding: 0 1rem;
}

.schedule-modal .card {
  border-radius: 18px;
  border: none;
}

/* 모달 안쪽 패딩 넉넉하게 */
.schedule-modal .card-header {
  padding: 1.25rem 1.75rem 1rem;
}

.schedule-modal .card-body {
  padding: 1.5rem 1.75rem 1.75rem;
}

/* 헤더 버튼 여백 */
.schedule-modal .card-header .btn {
  white-space: nowrap;
  padding-inline: 0.9rem;
}

/* 제목 스타일 살짝 */
.schedule-modal h5 {
  font-size: 1.1rem;
}

/* 시간 요약 박스 */
.time-summary {
  background: #f7f9fc;
}

/* 리스트 아이템 hover 느낌 살짝 */
.list-item-clickable {
  cursor: pointer;
}

.list-item-clickable:hover {
  background-color: #f8fafc;
}

/* 노션 느낌 뷰 전환 토글 */
.schedule-view-toggle {
  background: #f3f4f6;
  /* 연한 회색 배경 */
  border-radius: 999px;
  /* 완전한 캡슐 모양 */
  padding: 3px;
  border: 1px solid #e5e7eb;
  /* 아주 연한 테두리 */
  gap: 2px;
}

.schedule-view-toggle .toggle-btn {
  border: none;
  background: transparent;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
  /* 비활성 텍스트 (회색) */
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    color 0.15s ease,
    box-shadow 0.15s ease,
    transform 0.05s ease;
}

.schedule-view-toggle .toggle-btn:hover {
  background: #e5e7eb;
}

.schedule-view-toggle .toggle-btn.is-active {
  background: #ffffff;
  color: #111827;
  /* 활성 텍스트 (진한 회색) */
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.15);
}

.schedule-view-toggle .toggle-btn.is-active:active {
  transform: translateY(1px);
}

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
