<!-- src/views/studies/SchedulePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex flex-column align-items-center">
      <!-- 상단 헤더 -->
      <div
        class="d-flex align-items-center justify-content-between mb-4 w-100"
        style="max-width: 950px"
      >
        <h2 class="fw-bold mb-0">내가 만든 스터디 &gt; 일정</h2>

        <!-- ✅ 일정 추가 버튼: 모달 오픈 -->
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

          <div v-else-if="!groupedSchedules.length" class="py-5 text-center text-muted small">
            등록된 일정이 없습니다.
          </div>

          <div v-else class="schedule-wrapper">
            <!-- 날짜 그룹 -->
            <section
              v-for="group in groupedSchedules"
              :key="group.key"
              class="schedule-section"
            >
              <!-- 날짜 라벨 -->
              <div class="schedule-section-header px-4 py-2 text-muted small fw-semibold">
                {{ group.label }}
              </div>

              <!-- 일정 리스트 -->
              <div class="schedule-section-body">
                <div
                  v-for="item in group.items"
                  :key="item.id"
                  class="schedule-item d-flex align-items-center px-4"
                >
                  <!-- 시간 -->
                  <div class="schedule-time text-muted me-4">
                    {{ formatTime(item.start_at) }}
                  </div>

                  <!-- 내용 -->
                  <div class="flex-grow-1">
                    <div class="fw-semibold schedule-title text-truncate">
                      {{ item.title }}
                    </div>
                    <div class="text-muted small text-truncate">
                      {{ item.description }}
                    </div>
                  </div>

                  <!-- 액션 -->
                  <div class="ms-3 d-flex align-items-center gap-3 schedule-actions">
                    <!-- Edit 라우트 필요하면 나중에 열자 -->
                    <!--
                    <RouterLink
                      :to="`/studies/${studyId}/schedule/${item.id}/edit`"
                      class="text-decoration-none small text-primary"
                    >
                      Edit
                    </RouterLink>
                    -->
                    <button
                      type="button"
                      class="btn btn-link btn-sm text-danger text-decoration-none small px-0"
                      @click="onClickDelete(item.id)"
                    >
                      delete
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      <!-- ✅ 일정 추가 모달 -->
      <div v-if="showCreateModal" class="schedule-modal-backdrop">
        <div class="schedule-modal">
          <div class="card shadow-sm">
            <!-- 👉 닫기 버튼 제거, 제목만 -->
            <div class="card-header">
              <h5 class="mb-0 fw-bold">일정 추가</h5>
            </div>

            <div class="card-body">
              <!-- 에러 메시지 -->
              <div
                v-if="errorMessage"
                class="alert alert-danger py-2 small"
              >
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
                    placeholder="예) 카페에서 스터디"
                    maxlength="100"
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
                    placeholder="예) AI 수업 정리, 다음 주 과제 같이 하기"
                  ></textarea>
                </div>

                <!-- 시작 / 종료 -->
                <div class="row g-3">
                  <!-- 시작 -->
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
                        required
                      />
                    </div>
                  </div>

                  <!-- 종료 -->
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
                        required
                      />
                    </div>
                    <div class="form-text small">
                      종료 일시가 시작 일시보다 빠를 수 없습니다.
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const route = useRoute()
const studyId = route.params.id
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const schedules = ref([]) // 원본 일정 데이터
const isLoading = ref(false)

// ✅ 모달/폼 상태
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

// 날짜 포맷 도우미
const toKSTDate = (isoString) => {
  const d = new Date(isoString)
  return new Date(
    d.getFullYear(),
    d.getMonth(),
    d.getDate(),
    d.getHours(),
    d.getMinutes(),
    d.getSeconds()
  )
}

const formatTime = (isoString) => {
  const d = toKSTDate(isoString)
  const h = d.getHours().toString().padStart(2, '0')
  const m = d.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}

const formatDateLabel = (dateObj) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const target = new Date(dateObj)
  target.setHours(0, 0, 0, 0)

  const diffDays = Math.round((target - today) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '내일'

  const month = target.getMonth() + 1
  const day = target.getDate()
  return `${month}월 ${day}일`
}

// 오늘 기준으로 정렬 + 그룹핑
const groupedSchedules = computed(() => {
  if (!schedules.value.length) return []

  const sorted = [...schedules.value].sort(
    (a, b) => new Date(a.start_at) - new Date(b.start_at)
  )

  const map = new Map()

  for (const item of sorted) {
    const d = toKSTDate(item.start_at)
    const key = d.toISOString().slice(0, 10) // YYYY-MM-DD

    if (!map.has(key)) {
      map.set(key, {
        key,
        date: d,
        label: formatDateLabel(d),
        items: [],
      })
    }
    map.get(key).items.push(item)
  }

  return Array.from(map.values()).sort((a, b) => a.date - b.date)
})

const fetchSchedules = async () => {
  try {
    isLoading.value = true
    const res = await axios.get(`${API_BASE}/studies/${studyId}/schedules/`, {
      withCredentials: true,
    })
    // 기대 응답 예시:
    // [{ id, title, description, start_at, end_at }, ...]
    schedules.value = res.data || []
  } catch (error) {
    console.error('일정 목록 불러오기 실패', error)
  } finally {
    isLoading.value = false
  }
}

// 모달 열기/닫기 & 폼 초기화
const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
  }
  errorMessage.value = ''
}

const openCreateModal = () => {
  resetForm()
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

// datetime 문자열 조합: "YYYY-MM-DD HH:MM"
const buildDateTime = (date, time) => {
  if (!date || !time) return ''
  return `${date} ${time}`
}

const validateForm = () => {
  if (!form.value.title.trim()) {
    errorMessage.value = '일정 제목을 입력해주세요.'
    return false
  }

  const start = new Date(buildDateTime(form.value.startDate, form.value.startTime))
  const end = new Date(buildDateTime(form.value.endDate, form.value.endTime))

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    errorMessage.value = '시작/종료 일시를 올바르게 입력해주세요.'
    return false
  }

  if (end < start) {
    errorMessage.value = '종료 일시는 시작 일시보다 빠를 수 없습니다.'
    return false
  }

  errorMessage.value = ''
  return true
}

// 생성 요청
const onSubmitCreate = async () => {
  if (isSubmitting.value) return
  if (!validateForm()) return

  try {
    isSubmitting.value = true

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const payload = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      start_at: buildDateTime(form.value.startDate, form.value.startTime),
      end_at: buildDateTime(form.value.endDate, form.value.endTime),
    }

    await axios.post(
      `${API_BASE}/studies/${studyId}/schedules/study_schedule_create/`,
      payload,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      }
    )

    await fetchSchedules()
    closeCreateModal()
  } catch (error) {
    console.error('일정 생성 실패', error)
    errorMessage.value =
      error.response?.data?.detail || '일정 생성에 실패했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isSubmitting.value = false
  }
}

const onClickDelete = async (id) => {
  if (!confirm('이 일정을 삭제하시겠습니까?')) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await axios.delete(`${API_BASE}/studies/${studyId}/schedules/${id}/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
      },
    })

    schedules.value = schedules.value.filter((item) => item.id !== id)
  } catch (error) {
    console.error('일정 삭제 실패', error)
    alert('일정 삭제에 실패했습니다.')
  }
}

onMounted(async () => {
  await ensureCsrf()
  await fetchSchedules()
})
</script>

<style scoped>
/* 카드 전체 배경을 연한 회색 분위기로 */
.schedule-card {
  border: none;
  background-color: #f6f7fb;
}

/* 날짜 섹션 간 간격 */
.schedule-section + .schedule-section {
  border-top: 1px solid #e0e3ec;
}

/* 날짜 라벨 줄 */
.schedule-section-header {
  background-color: transparent;
}

/* 섹션 하위 아이템 래퍼 */
.schedule-section-body {
  background-color: #ffffff;
}

/* 개별 일정 줄 */
.schedule-item {
  min-height: 64px;
  border-top: 1px solid #f0f1f6;
}

/* 첫 번째 일정은 위 보더 제거 */
.schedule-section-body .schedule-item:first-of-type {
  border-top: 1px solid #e0e3ec;
}

.schedule-time {
  width: 70px;
  font-weight: 500;
}

.schedule-title {
  font-size: 0.98rem;
}

/* 액션 버튼들 조금 붙여주기 */
.schedule-actions .btn-link,
.schedule-actions a {
  font-weight: 500;
}

/* ✅ 모달 스타일 */
.schedule-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200; /* 네비게이션바보다 위로 */
}

.schedule-modal {
  width: 100%;
  max-width: 640px;
}

/* 카드 모서리 조금 더 둥글게 */
.schedule-modal .card {
  border-radius: 16px;
}
</style>
