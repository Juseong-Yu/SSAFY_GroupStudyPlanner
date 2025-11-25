<!-- src/views/studies/SchedulePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex flex-column align-items-center">
      <!-- 상단 헤더 -->
      <div
        class="d-flex align-items-center justify-content-between mb-2 w-100"
        style="max-width: 1000px"
      >
        <div>
          <h2 class="fw-bold mb-0">스터디 일정</h2>
        </div>

        <!-- 일정 추가 버튼 -->
        <button
          type="button"
          class="btn btn-outline-primary btn-sm"
          @click="openCreateModal"
        >
          + 일정 추가
        </button>
      </div>

      <!-- 상태 요약 배지 -->
      <div class="w-100 mb-4" style="max-width: 1000px">
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

      <!-- 본문: 왼쪽 캘린더, 오른쪽 일정 카드들 -->
      <div class="w-100" style="max-width: 1000px">
        <div class="row g-4">
          <!-- 왼쪽: FullCalendar -->
          <div class="col-12 col-lg-7">
            <div class="card shadow-sm">
              <div class="card-body p-3">
                <div v-if="isLoading && !isMounted" class="py-5 text-center text-muted small">
                  불러오는 중...
                </div>
                <div v-else-if="isMounted" class="calendar-wrapper">
                  <FullCalendar :options="calendarOptions" />
                </div>
              </div>
            </div>
          </div>

          <!-- 오른쪽: 진행중 / 다가오는 / 지난 일정 -->
          <div class="col-12 col-lg-5">
            <!-- 진행중 일정 -->
            <div class="card shadow-sm mb-3" v-if="ongoingSchedules.length || isLoading">
              <div
                class="card-header d-flex align-items-center justify-content-between schedule-section-header-today"
              >
                <span class="fw-semibold small">진행중인 일정</span>
                <span class="badge bg-primary-subtle text-primary small">
                  {{ ongoingSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div
                  v-if="!ongoingSchedules.length && !isLoading"
                  class="py-3 text-center text-muted small"
                >
                  진행중인 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div
                    v-for="item in ongoingSchedules"
                    :key="'ongoing-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)"
                  >
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
                        <span
                          class="badge rounded-pill bg-primary-subtle text-primary small"
                        >
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
              <div
                class="card-header d-flex align-items-center justify-content-between"
              >
                <span class="fw-semibold small">다가오는 일정</span>
                <span class="badge bg-success-subtle text-success small">
                  {{ upcomingSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div
                  v-if="!upcomingSchedules.length && !isLoading"
                  class="py-3 text-center text-muted small"
                >
                  다가오는 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div
                    v-for="item in upcomingSchedules"
                    :key="'upcoming-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)"
                  >
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
                        <span
                          v-if="getDDay(item) !== null"
                          class="badge rounded-pill bg-success-subtle text-success small"
                        >
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
              <div
                class="card-header d-flex align-items-center justify-content-between"
              >
                <span class="fw-semibold small">지난 일정</span>
                <span class="badge bg-secondary-subtle text-secondary small">
                  {{ pastSchedules.length }}
                </span>
              </div>
              <div class="card-body p-0">
                <div
                  v-if="!pastSchedules.length && !isLoading"
                  class="py-3 text-center text-muted small"
                >
                  지난 일정이 없습니다.
                </div>
                <div v-else class="list-group list-group-flush">
                  <div
                    v-for="item in pastSchedules.slice(0, 5)"
                    :key="'past-' + item.id"
                    class="list-group-item d-flex align-items-start list-item-clickable"
                    @click="openDetailModal(item.id)"
                  >
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
                  <div
                    v-if="pastSchedules.length > 5"
                    class="list-group-item text-center small text-muted"
                  >
                    지난 일정 더보기 ({{ pastSchedules.length - 5 }}개)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ====================== -->
      <!-- 일정 상세 모달 (왼쪽 정보 / 오른쪽 시간 요약) -->
      <!-- ====================== -->
      <div v-if="showDetailModal" class="schedule-modal-backdrop">
        <div class="schedule-modal">
          <div class="card shadow-sm">
            <div
              class="card-header d-flex justify-content-between align-items-start flex-wrap gap-2"
            >
              <div>
                <h5 class="mb-1 fw-bold">
                  {{ detail?.schedule.title || "일정 상세" }}
                </h5>
                <!-- 🔥 제목 밑 시간 요약(중복) 제거 -->
                <!-- <p v-if="detail" class="mb-0 small text-muted">
                  {{ formatRangeUtc(detail.schedule.start_at, detail.schedule.end_at) }}
                </p> -->
              </div>
              <div class="d-flex align-items-center gap-2 ms-auto">
                <button
                  v-if="detail"
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  @click="onClickDeleteFromDetail"
                >
                  삭제
                </button>
                <button
                  v-if="detail"
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  @click="toggleEditMode"
                >
                  {{ isEditMode ? "수정 취소" : "수정" }}
                </button>
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
              <div v-if="isDetailLoading" class="py-4 text-center text-muted small">
                불러오는 중...
              </div>

              <template v-else-if="detail">
                <!-- 보기 모드: 왼쪽 정보 / 오른쪽 시간 요약 -->
                <div v-if="!isEditMode" class="row g-4 align-items-start">
                  <!-- 왼쪽: 정보 영역 -->
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
                        {{ detail.schedule.description || "내용 없음" }}
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
                        <div>{{ formatShortDateUtc(detail.schedule.start_at) }}</div>
                        <div>{{ formatTimeUtc(detail.schedule.start_at) }}</div>
                      </div>

                      <div>
                        <div class="text-muted fw-semibold mb-1">종료</div>
                        <div>
                          {{
                            formatShortDateUtc(
                              detail.schedule.end_at || detail.schedule.start_at
                            )
                          }}
                        </div>
                        <div>
                          {{
                            formatTimeUtc(
                              detail.schedule.end_at || detail.schedule.start_at
                            )
                          }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 수정 모드: 전체 폭 사용 -->
                <div v-else>
                  <div
                    v-if="editErrorMessage"
                    class="alert alert-danger py-2 small mb-3"
                  >
                    {{ editErrorMessage }}
                  </div>

                  <form @submit.prevent="onSubmitUpdate">
                    <div class="mb-3">
                      <label class="form-label fw-semibold small">일정 제목</label>
                      <input
                        v-model="editForm.title"
                        type="text"
                        class="form-control"
                        required
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label fw-semibold small">일정 상세</label>
                      <textarea
                        v-model="editForm.description"
                        class="form-control"
                        rows="3"
                      ></textarea>
                    </div>

                    <div class="row g-3">
                      <div class="col-md-6">
                        <label class="form-label fw-semibold small">시작 일시</label>
                        <div class="d-flex gap-2">
                          <input
                            v-model="editForm.startDate"
                            type="date"
                            class="form-control"
                            required
                          />
                          <input
                            v-model="editForm.startTime"
                            type="time"
                            class="form-control"
                          />
                        </div>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label fw-semibold small">종료 일시</label>
                        <div class="d-flex gap-2">
                          <input
                            v-model="editForm.endDate"
                            type="date"
                            class="form-control"
                            required
                          />
                          <input
                            v-model="editForm.endTime"
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
                        @click="toggleEditMode"
                      >
                        취소
                      </button>
                      <button
                        type="submit"
                        class="btn btn-primary btn-sm"
                        :disabled="isUpdating"
                      >
                        {{ isUpdating ? "수정 중..." : "수정 저장" }}
                      </button>
                    </div>
                  </form>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- ====================== -->
      <!-- 일정 추가 모달 -->
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
                  <input
                    v-model="form.title"
                    type="text"
                    class="form-control"
                    required
                  />
                </div>

                <!-- 상세 -->
                <div class="mb-4">
                  <label class="form-label fw-semibold">일정 상세</label>
                  <textarea
                    v-model="form.description"
                    class="form-control"
                    rows="3"
                  ></textarea>
                </div>

                <!-- 시작 / 종료 -->
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

                <!-- 버튼 -->
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
                    {{ isSubmitting ? "저장 중..." : "저장" }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <!-- 모달 끝 -->
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import axios from "axios"
import AppShell from "@/layouts/AppShell.vue"
import { ensureCsrf, getCookie } from "@/utils/csrf_cors"

import FullCalendar from "@fullcalendar/vue3"
import dayGridPlugin from "@fullcalendar/daygrid"
import interactionPlugin from "@fullcalendar/interaction"
import type { CalendarOptions } from "@fullcalendar/core"

const route = useRoute()
const studyId = route.params.id as string
const API_BASE = import.meta.env.VITE_API_BASE_URL || ""

/* ==============================
   타입 정의
================================= */

interface ScheduleCore {
  id?: number
  title: string
  description: string
  start_at: string   // ISO UTC
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

interface ScheduleDetail {
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
const isMounted = ref(false)

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

/* 상세 모달 상태 */
const showDetailModal = ref(false)
const isDetailLoading = ref(false)
const detailError = ref("")
const detail = ref<ScheduleDetail | null>(null)

const isEditMode = ref(false)
const isUpdating = ref(false)
const editErrorMessage = ref("")

const editForm = ref({
  title: "",
  description: "",
  startDate: "",
  startTime: "",
  endDate: "",
  endTime: "",
})

/* ==============================
   FullCalendar 옵션
================================= */

const calendarOptions = ref<CalendarOptions>({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: "dayGridMonth",
  height: "auto",
  locale: "ko",
  selectable: true,
  timeZone: "UTC",
  events: [],
  dateClick: (info) => {
    console.log("dateClick:", info.dateStr)
  },
})

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

    // FullCalendar 이벤트 세팅
    const fcEvents = schedules.value.map((item) => {
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
        backgroundColor: '#e7f1ff', // 아주 연한 파랑
        borderColor: '#b6d4fe',     // 보통 파랑
        textColor: '#084298',
      }
    })

    calendarOptions.value.events = fcEvents
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
        headers: { "X-CSRFToken": csrftoken },
      }
    )

    schedules.value = schedules.value.filter((i) => i.id !== id)
    await fetchSchedules()
  } catch {
    alert("삭제에 실패했습니다.")
  }
}

/* ==============================
   상세 조회 / 수정
================================= */

const openDetailModal = async (id: number) => {
  showDetailModal.value = true
  isDetailLoading.value = true
  detailError.value = ""
  isEditMode.value = false
  editErrorMessage.value = ""
  detail.value = null

  try {
    const res = await axios.get<ScheduleDetail>(
      `${API_BASE}/studies/${studyId}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
      }
    )
    detail.value = res.data

    // editForm 초기값 세팅
    const s = parseUtc(res.data.schedule.start_at)
    const e = parseUtc(res.data.schedule.end_at || res.data.schedule.start_at)

    const toInputDate = (d: Date): string =>
      isNaN(d.getTime()) ? "" : d.toISOString().slice(0, 10)
    const toInputTime = (d: Date): string =>
      isNaN(d.getTime()) ? "" : d.toISOString().slice(11, 16)

    editForm.value = {
      title: res.data.schedule.title,
      description: res.data.schedule.description,
      startDate: toInputDate(s),
      startTime: toInputTime(s),
      endDate: toInputDate(e),
      endTime: toInputTime(e),
    }
  } catch (e) {
    console.error(e)
    detailError.value = "일정 상세를 불러오지 못했습니다."
  } finally {
    isDetailLoading.value = false
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  detail.value = null
  isEditMode.value = false
  editErrorMessage.value = ""
}

const toggleEditMode = () => {
  if (!detail.value) return
  isEditMode.value = !isEditMode.value
  editErrorMessage.value = ""
}

const validateEditForm = (): boolean => {
  const startStr = buildDateTime(
    editForm.value.startDate,
    editForm.value.startTime,
    "00:00"
  )
  const endStr = buildDateTime(
    editForm.value.endDate,
    editForm.value.endTime,
    "23:59"
  )

  if (!startStr || !endStr) {
    editErrorMessage.value = "날짜를 입력해주세요."
    return false
  }

  const start = new Date(startStr)
  const end = new Date(endStr)

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    editErrorMessage.value = "날짜/시간 형식이 올바르지 않습니다."
    return false
  }

  if (end < start) {
    editErrorMessage.value = "종료 시간이 더 빠릅니다."
    return false
  }

  editErrorMessage.value = ""
  return true
}

const onSubmitUpdate = async () => {
  if (!detail.value) return
  if (!validateEditForm()) return

  try {
    isUpdating.value = true
    await ensureCsrf()
    const csrftoken = getCookie("csrftoken")

    const start_at = buildDateTime(
      editForm.value.startDate,
      editForm.value.startTime,
      "00:00"
    )
    const end_at = buildDateTime(
      editForm.value.endDate,
      editForm.value.endTime,
      "23:59"
    )

    await axios.put(
      `${API_BASE}/studies/${studyId}/schedules/${detail.value.id}/study_schedule_detail/`,
      {
        id: detail.value.id,
        title: editForm.value.title.trim(),
        description: editForm.value.description.trim(),
        start_at,
        end_at,
      },
      {
        withCredentials: true,
        headers: {
          "X-CSRFToken": csrftoken,
          "Content-Type": "application/json",
        },
      }
    )

    // 리스트/캘린더 갱신
    await fetchSchedules()

    // 상세 데이터도 프론트에서 동기화
    if (detail.value) {
      detail.value.schedule.title = editForm.value.title.trim()
      detail.value.schedule.description = editForm.value.description.trim()
      detail.value.schedule.start_at = start_at
      detail.value.schedule.end_at = end_at
    }

    isEditMode.value = false
  } catch (e) {
    console.error(e)
    editErrorMessage.value = "일정 수정에 실패했습니다."
  } finally {
    isUpdating.value = false
  }
}

const onClickDeleteFromDetail = async () => {
  if (!detail.value) return
  await onClickDelete(detail.value.id)
  closeDetailModal()
}

/* ==============================
   생성 관련
================================= */

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

const buildDateTime = (date: string, time: string, fallback: string): string => {
  const d = (date || "").trim()
  if (!d) return ""
  const t = (time || "").trim() || fallback
  return `${d} ${t}`
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

    const start_at = buildDateTime(form.value.startDate, form.value.startTime, "00:00")
    const end_at = buildDateTime(form.value.endDate, form.value.endTime, "23:59")

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
          "X-CSRFToken": csrftoken,
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
   계산된 값 / computed
================================= */

const detailAuthorAvatar = computed(() => {
  if (!detail.value || !detail.value.author.profile_img) return null
  return `${API_BASE}${detail.value.author.profile_img}`
})

/* ==============================
   Mount
================================= */
onMounted(async () => {
  isMounted.value = true
  await ensureCsrf()
  await fetchSchedules()

  // FullCalendar 이벤트 클릭 → 상세 모달
  calendarOptions.value.eventClick = (info: any) => {
    const id = Number(info.event.id)
    if (!Number.isNaN(id)) {
      openDetailModal(id)
    }
  }
})
</script>

<style scoped>
.calendar-wrapper :deep(.fc) {
  background-color: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0.5rem;
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

/* 날짜 숫자 파란색 → 일반 텍스트 색으로 */
:deep(.fc .fc-daygrid-day-number) {
  color: #212529;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-day-number:hover),
:deep(.fc .fc-daygrid-day-number:focus) {
  color: #212529;
}

:deep(.fc .fc-daygrid-event) {
  color: #212529;
}

:deep(.fc .fc-daygrid-day:hover) {
  background: #fafcff;
}

:deep(.fc .fc-daygrid-event a) {
  color: inherit;
  text-decoration: none;
}

/* 요일 헤더(월화수목금토일) 색상 원래대로 */
:deep(.fc .fc-col-header-cell-cushion) {
  color: #3b4b70;
  text-decoration: none;
}

:deep(.fc .fc-col-header-cell-cushion:hover),
:deep(.fc .fc-col-header-cell-cushion:focus) {
  color: #3b4b70;
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

/* 공통 모달 백드롭 */
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

.schedule-modal p.small.text-muted {
  margin-top: 0.15rem;
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
</style>
