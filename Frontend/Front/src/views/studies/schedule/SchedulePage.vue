<!-- src/views/studies/SchedulePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex flex-column align-items-center">
      <!-- 상단 헤더 -->
      <div
        class="d-flex align-items-center justify-content-between mb-4 w-100"
        style="max-width: 950px"
      >
        <h2 class="fw-bold mb-0"> 일정</h2>

        <!-- 일정 추가 버튼 -->
        <button
          type="button"
          class="btn btn-outline-primary btn-sm"
          @click="openCreateModal"
        >
          + 일정 추가
        </button>
      </div>

      <!-- 본문 카드 -->
      <div class="card shadow-sm w-100 schedule-card" style="max-width: 950px">
        <div class="card-body p-0">
          <div v-if="isLoading" class="py-5 text-center text-muted small">
            불러오는 중...
          </div>

          <div
            v-else-if="!upcomingSchedules.length"
            class="py-5 text-center text-muted small"
          >
            예정된 일정이 없습니다.
          </div>

          <div v-else class="schedule-wrapper">
            <!-- 🔵 날짜 그룹 -->
            <section
              v-for="group in groupedSchedules"
              :key="group.key"
              class="schedule-section"
            >
              <!-- 날짜 라벨 -->
              <div
                class="schedule-section-header px-4 py-2 small fw-semibold"
                :class="{ 'schedule-section-header-today': group.isToday }"
              >
                {{ group.label }}
              </div>

              <!-- 일정 리스트 -->
              <div class="schedule-section-body">
                <div
                  v-for="item in group.items"
                  :key="item.id"
                  class="schedule-item d-flex align-items-center px-4"
                >
                  <div class="schedule-time text-muted me-4">
                    {{ formatTime(item.schedule.start_at) }}
                  </div>

                  <div class="flex-grow-1">
                    <div class="fw-semibold schedule-title text-truncate">
                      {{ item.schedule.title }}
                    </div>
                    <div class="text-muted small text-truncate">
                      {{ item.schedule.description }}
                    </div>
                  </div>

                  <button
                    class="btn btn-link btn-sm text-danger px-0"
                    @click="onClickDelete(item.id)"
                  >
                    delete
                  </button>
                </div>
              </div>
            </section>
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
                      <input v-model="form.startDate" type="date" class="form-control" required />
                      <input v-model="form.startTime" type="time" class="form-control" required />
                    </div>
                  </div>

                  <div class="col-md-6">
                    <label class="form-label fw-semibold">종료 일시</label>
                    <div class="d-flex gap-2">
                      <input v-model="form.endDate" type="date" class="form-control" required />
                      <input v-model="form.endTime" type="time" class="form-control" required />
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
                    {{ isSubmitting ? '저장 중...' : '저장' }}
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

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import axios from "axios"
import AppShell from "@/layouts/AppShell.vue"
import { ensureCsrf, getCookie } from "@/utils/csrf_cors"

const route = useRoute()
const studyId = route.params.id
const API_BASE = import.meta.env.VITE_API_BASE_URL || ""

const schedules = ref([])
const isLoading = ref(false)

/* 모달 상태 */
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

/* ==============================
   날짜 유틸
================================= */
const toKST = (iso) => new Date(iso)

const todayZero = () => {
  const t = new Date()
  t.setHours(0, 0, 0, 0)
  return t
}

const formatTime = (iso) => {
  const d = toKST(iso)
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`
}

const formatDateLabel = (d) => {
  const t = todayZero()
  const day = new Date(d)
  day.setHours(0, 0, 0, 0)

  if (day.getTime() === t.getTime()) return "오늘"
  if (day.getTime() === t.getTime() + 86400000) return "내일"
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}

/* ==============================
   일정 필터링 & 그룹핑
================================= */

/* 🔵 오늘 이후 일정만 */
const upcomingSchedules = computed(() => {
  const base = todayZero()
  return schedules.value.filter((item) => new Date(item.schedule.start_at) >= base)
})

/* 🔵 날짜 그룹 */
const groupedSchedules = computed(() => {
  if (!upcomingSchedules.value.length) return []

  const sorted = [...upcomingSchedules.value].sort(
    (a, b) => new Date(a.schedule.start_at) - new Date(b.schedule.start_at)
  )

  const base = todayZero()
  const map = new Map()

  for (const item of sorted) {
    const d = toKST(item.schedule.start_at)
    const key = d.toISOString().slice(0, 10)

    if (!map.has(key)) {
      const dateOnly = new Date(d)
      dateOnly.setHours(0, 0, 0, 0)

      map.set(key, {
        key,
        date: d,
        isToday: dateOnly.getTime() === base.getTime(),
        label: formatDateLabel(d),
        items: [],
      })
    }
    map.get(key).items.push(item)
  }

  return Array.from(map.values()).sort((a, b) => a.date - b.date)
})

/* ==============================
   CRUD API
================================= */

const fetchSchedules = async () => {
  try {
    isLoading.value = true
    const res = await axios.get(
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

const onClickDelete = async (id) => {
  if (!confirm("삭제하시겠습니까?")) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie("csrftoken")

    await axios.delete(`${API_BASE}/studies/${studyId}/schedules/${id}/`, {
      withCredentials: true,
      headers: { "X-CSRFToken": csrftoken },
    })

    schedules.value = schedules.value.filter((i) => i.id !== id)
  } catch {
    alert("삭제에 실패했습니다.")
  }
}

/* 생성 */
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

const buildDateTime = (date, time) => `${date} ${time}`

const validateForm = () => {
  const start = new Date(buildDateTime(form.value.startDate, form.value.startTime))
  const end = new Date(buildDateTime(form.value.endDate, form.value.endTime))
  if (end < start) return (errorMessage.value = "종료 시간이 더 빠릅니다.")
  return true
}

const onSubmitCreate = async () => {
  if (!validateForm()) return

  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie("csrftoken")

    await axios.post(
      `${API_BASE}/studies/${studyId}/schedules/study_schedule_create/`,
      {
        title: form.value.title.trim(),
        description: form.value.description.trim(),
        start_at: buildDateTime(form.value.startDate, form.value.startTime),
        end_at: buildDateTime(form.value.endDate, form.value.endTime),
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
   Mount
================================= */
onMounted(async () => {
  await ensureCsrf()
  await fetchSchedules()
})
</script>

<style scoped>
.schedule-card {
  border: none;
  background-color: #f6f7fb;
}

.schedule-section + .schedule-section {
  border-top: 1px solid #e0e3ec;
}

.schedule-section-header {
  background: transparent;
}

.schedule-section-header-today {
  background: #eef4ff;
  color: #1d4ed8;
}

.schedule-item {
  min-height: 56px;
  border-top: 1px solid #f0f1f6;
}

.schedule-time {
  width: 110px;
  font-weight: 500;
  font-size: 0.8rem;
}

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
  max-width: 640px;
}

.schedule-modal .card {
  border-radius: 16px;
}
</style>
