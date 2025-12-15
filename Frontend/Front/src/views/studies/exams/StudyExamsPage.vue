<!-- src/views/studies/exams/StudyExamsPage.vue -->
<template>
  <AppShell>
    <!-- ✅ 다른 스터디 페이지들과 동일한 레이아웃 패턴 적용 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper">
        <!-- 상단 헤더 -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="fw-bold mb-0">시험 전체보기</h2>

          <!-- 리더만 시험 생성 버튼 표시 -->
          <button v-if="isPrivileged" type="button" class="btn btn-light-outline btn-sm" @click="openCreateModal">
            + 시험 생성
          </button>
        </div>

        <!-- 시험 리스트 카드 -->
        <div class="card shadow-sm exam-card w-100">
          <div class="card-body p-0">
            <div v-if="loading" class="text-center text-muted py-4">
              시험 목록 불러오는 중...
            </div>

            <div v-else-if="exams.length === 0" class="text-center text-muted py-5">
              아직 등록된 시험이 없습니다.
            </div>

            <template v-else>
              <!-- 리스트 (공지 테이블 느낌으로 여백 넉넉하게) -->
              <ul class="list-group list-group-flush mb-0">
                <li v-for="exam in pagedExams" :key="exam.id"
                  class="list-group-item exam-list-item d-flex justify-content-between align-items-center ms-1">
                  <!-- 왼쪽: 제목 / 시작·마감 / 뱃지들 -->
                  <div class="exam-left">
                    <div class="fw-semibold exam-title text-truncate">
                      <button type="button" class="exam-title-btn text-truncate" @click="handleExamTitleClick(exam)">
                        {{ exam.title }}
                      </button>
                    </div>

                    <!-- 시작/마감 시간 줄(항상 높이 유지) -->
                    <div class="small text-muted exam-time-row">
                      <template v-if="exam.start_at || exam.due_at">
                        <span v-if="exam.start_at">
                          시작: {{ formatDateTime(exam.start_at) }}
                        </span>
                        <span v-if="exam.start_at && exam.due_at"> · </span>
                        <span v-if="exam.due_at">
                          마감: {{ formatDateTime(exam.due_at) }}
                        </span>
                      </template>

                      <!-- 시간 없음 → 공간만 차지 -->
                      <template v-else>
                        <span class="placeholder-line">&nbsp;</span>
                      </template>
                    </div>

                    <div class="mt-1 d-flex flex-wrap gap-2 small">
                      <!-- 공개 범위 뱃지 -->
                      <span class="badge bg-secondary-subtle text-secondary">
                        {{ exam.visibility_label }}
                      </span>

                      <!-- 응시 여부 뱃지 -->
                      <span v-if="exam.has_taken" class="badge bg-success-subtle text-success">
                        응시 완료
                      </span>
                      <span v-else class="badge bg-primary-subtle text-primary">
                        미응시
                      </span>
                    </div>
                  </div>

                  <!-- 오른쪽: 액션 버튼 -->
                  <div class="text-end exam-right">
                    <!-- ✅ 리더 / admin: 시험 응시 + 결과 확인 -->
                    <template v-if="isPrivileged">
                      <div class="d-flex gap-2 justify-content-end">
                        <!-- 아직 응시 안 했고, 시험 시간이면만 응시 버튼 노출 -->
                        <button v-if="!exam.has_taken && isExamOpen(exam)" type="button"
                          class="btn btn-light-outline btn-sm" @click="handleExamClick(exam)">
                          시험 응시
                        </button>

                        <!-- 항상 노출: 결과 확인 (미리보기 / 내 결과 확인 공통) -->
                        <button type="button" class="btn btn-primary-outline btn-sm" @click="openResultModal(exam)">
                          결과 확인
                        </button>
                      </div>
                    </template>

                    <!-- ✅ 일반 멤버 -->
                    <template v-else>
                      <!-- 이미 응시한 시험: 항상 응시 내역 보기 -->
                      <button v-if="exam.has_taken" type="button" class="btn btn-primary-outline btn-sm"
                        @click="handleExamClick(exam)">
                        응시 내역 보기
                      </button>

                      <!-- 아직 응시 안 했고, 시험 시간이면만 응시 버튼 노출 -->
                      <button v-else-if="isExamOpen(exam)" type="button" class="btn btn-primary-outline btn-sm"
                        @click="handleExamClick(exam)">
                        시험 응시
                      </button>
                      <!-- v-else면 아무 버튼도 안 보임 (시험 시간이 아님) -->
                    </template>
                  </div>
                </li>
              </ul>
            </template>
          </div>
        </div>

        <!-- ✅ 페이지네이션 (공지 페이지랑 동일한 느낌) -->
        <div v-if="totalPages > 0 && exams.length > 0"
          class="pagination-wrapper d-flex flex-column flex-md-row align-items-center justify-content-between gap-2 mt-3 w-100">
          <div class="text-muted small">
            총 <span class="fw-semibold">{{ total }}</span>개 ·
            <span class="fw-semibold">{{ currentPage }}</span> /
            {{ totalPages }} 페이지
          </div>

          <nav aria-label="시험 페이지 이동">
            <ul class="pagination pagination-sm mb-0">
              <!-- Prev -->
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link icon-btn" @click="goPrev" :disabled="currentPage === 1" type="button">
                  <i class="bi bi-chevron-left" aria-hidden="true"></i>
                </button>
              </li>

              <!-- 페이지 번호 -->
              <li v-for="p in pageWindow" :key="p" class="page-item" :class="{ active: p === currentPage }">
                <button class="page-link" @click="goPage(p)" type="button">
                  {{ p }}
                </button>
              </li>

              <!-- Next -->
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link icon-btn" @click="goNext" :disabled="currentPage === totalPages" type="button">
                  <i class="bi bi-chevron-right" aria-hidden="true"></i>
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- 시험 생성 모달 -->
    <ExamCreateModal v-if="showCreateModal" :study-id="studyId" @close="showCreateModal = false" />

    <!-- 응시 결과 모달 -->
    <ExamResultModal v-if="showResultModal" :visible="showResultModal" :my-result="myResult" :scoreboard="scoreboard"
      :all-results-detail="allResultsDetail" :can-see-own-detail="canSeeOwnDetail"
      :can-see-scoreboard="canSeeScoreboard" :can-see-others-detail="canSeeOthersDetail" :is-leader="isPrivileged"
      :problems="selectedExamProblems" :exam-title="selectedExamTitle" @close="showResultModal = false" />
  </AppShell>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
import AppShell from '@/layouts/AppShell.vue'
import ExamCreateModal from '@/views/studies/exams/components/ExamCreateModal.vue'
import ExamResultModal from '@/views/studies/exams/components/ExamResultModal.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import { useStudyRoleStore } from '@/stores/studyRoleStore'
import { useUserStore } from '@/stores/user'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

// 라우트에서 studyId 가져오기
const studyId = Number(route.params.studyId)

type VisibilityType = 'public' | 'score_only' | 'private'

interface ExamListItem {
  id: number
  title: string
  start_at: string | null
  due_at: string | null
  visibility: VisibilityType
  visibility_label: string
  has_taken: boolean
}

// exam_detail / my_result 에서 내려올 문제 타입
interface Problem {
  id: number
  order: number
  text: string
  choices: string[] | null
}

const exams = ref<ExamListItem[]>([])
const loading = ref(false)
const showCreateModal = ref(false)

// ===== 역할 (리더 여부) - Pinia =====
const studyRoleStore = useStudyRoleStore()
const userStore = useUserStore()

const isLeader = computed(() => studyRoleStore.isLeader(String(studyId)))
const isAdmin = computed(() => studyRoleStore.isAdmin(String(studyId)))
const isPrivileged = computed(() => isLeader.value || isAdmin.value)

// ===== 시험 결과 모달 관련 상태 =====
const showResultModal = ref(false)
const selectedExamId = ref<number | null>(null)
const selectedExamTitle = ref<string>('')
const selectedExamProblems = ref<Problem[]>([])

// exam visibility + 권한 플래그
const examVisibility = ref<VisibilityType>('public')

// my_result / scoreboard / all_results_detail
const myResult = ref<any | null>(null)
const scoreboard = ref<any[]>([])
const allResultsDetail = ref<any[]>([])

// ✅ 페이지네이션 상태
const pageSize = ref(8)
const currentPage = ref(1)

const total = computed(() => exams.value.length)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / pageSize.value)),
)

const pagedExams = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return exams.value.slice(start, start + pageSize.value)
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

// 권한 플래그 (리더+admin + visibility 기반)
const canSeeOwnDetail = computed(() => {
  if (isPrivileged.value) return true

  if (examVisibility.value === 'public') return true
  if (examVisibility.value === 'score_only') return true
  if (examVisibility.value === 'private') return false
  return false
})

const canSeeScoreboard = computed(() => {
  if (isPrivileged.value) return true
  if (examVisibility.value === 'public') return true
  return false
})

const canSeeOthersDetail = computed(() => {
  return isPrivileged.value
})

// ===== 공통 유틸 =====
const openCreateModal = () => {
  showCreateModal.value = true
}

const formatDateTime = (iso: string | null) => {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''

  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

/**
 * ✅ 지금 시점에 시험 응시 가능한지 여부
 */
const isExamOpen = (exam: ExamListItem): boolean => {
  const now = Date.now()

  let start: number | null = null
  let due: number | null = null

  if (exam.start_at) {
    const t = new Date(exam.start_at).getTime()
    start = Number.isNaN(t) ? null : t
  }
  if (exam.due_at) {
    const t = new Date(exam.due_at).getTime()
    due = Number.isNaN(t) ? null : t
  }

  if (start !== null && now < start) return false
  if (due !== null && now > due) return false
  return true
}

// 공개 범위 → 라벨 매핑
const visibilityLabelMap: Record<VisibilityType, string> = {
  public: '전체 공개',
  score_only: '점수만 공개',
  private: '비공개',
}

// ===== 시험 목록 불러오기 =====
const fetchExams = async () => {
  loading.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const res = await client.get(`${API_BASE}/studies/${studyId}/exams/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken,
      },
    })

    exams.value = res.data.map((exam: any): ExamListItem => ({
      id: exam.id,
      title: exam.title,
      start_at: exam.start_at ?? null,
      due_at: exam.due_at ?? null,
      visibility: exam.visibility as VisibilityType,
      visibility_label: exam.visibility_label
        ? exam.visibility_label
        : visibilityLabelMap[exam.visibility as VisibilityType] ?? '전체 공개',
      has_taken: Boolean(exam.has_taken),
    }))

    currentPage.value = 1
  } finally {
    loading.value = false
  }
}

// ===== 버튼 클릭: 응시 / 응시 내역 보기 =====
const handleExamClick = (exam: ExamListItem) => {
  // 아직 응시 안 했는데 시험 시간이 아니면 방어
  if (!exam.has_taken && !isExamOpen(exam)) {
    alert('지금은 시험 응시 시간이 아닙니다.')
    return
  }

  if (!exam.has_taken) {
    router.push({
      name: 'ExamTake',
      params: {
        studyId,
        examId: exam.id,
      },
    })
    return
  }

  // 이미 응시한 시험이면 → 결과 모달 열기
  openResultModal(exam)
}

// 제목 클릭 시: 응시 이후면 아무 행동도 하지 않음
const handleExamTitleClick = (exam: ExamListItem) => {
  // ❌ 이미 응시했으면 타이틀 클릭 시 아무 일도 일어나지 않음
  if (exam.has_taken) {
    return
  }

  // ❌ 아직 응시 안 했고, 시험 열리지 않았으면 아무 일도 없음
  if (!isExamOpen(exam)) {
    return
  }

  // ⭕ 응시 가능할 때만 응시 페이지로 이동
  handleExamClick(exam)
}


// ===== 응시 결과 모달 열기: 내 결과 가져오기 =====
const openResultModal = async (exam: ExamListItem) => {
  try {
    selectedExamId.value = exam.id
    selectedExamTitle.value = exam.title

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // 백엔드에 /my_result/ 같은 엔드포인트 구현 가정
    // 예: GET /studies/<study_id>/exams/<exam_id>/my_result/
    const res = await client.get(
      `${API_BASE}/studies/${studyId}/exams/${exam.id}/my_result/`,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      },
    )

    const data = res.data as {
      visibility: VisibilityType
      my_result: any | null
      scoreboard?: any[]
      all_results_detail?: any[]
      questions?: {
        id: number
        order: number
        text: string
        choices: string[] | null
      }[]
    }

    examVisibility.value = data.visibility
    myResult.value = data.my_result
    scoreboard.value = data.scoreboard ?? []
    allResultsDetail.value = data.all_results_detail ?? []

    selectedExamProblems.value =
      data.questions?.map((q) => ({
        id: q.id,
        order: q.order,
        text: q.text,
        choices: q.choices,
      })) ?? []

    showResultModal.value = true
  } catch (err: any) {
    console.error(err)
    alert(err.response?.data?.detail || '시험 결과 조회 중 오류가 발생했습니다.')
  }
}

onMounted(() => {
  fetchExams()
})
</script>

<style scoped>
.study-page-wrapper {
  width: 100%;
  max-width: 1300px;
  padding-left: 0.5rem;
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

/* 카드/리스트 느낌 공지랑 맞추기 */
.exam-card {
  overflow: hidden;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.exam-list-item {
  padding-top: 0.9rem;
  padding-bottom: 0.9rem;
}

.exam-left {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding-right: 1rem;
  min-width: 0;
}

.exam-title {
  max-width: 520px;
}

/* 시간 줄: 항상 같은 높이 */
.exam-time-row {
  min-height: 20px;
  display: flex;
  align-items: center;
  margin-top: 2px;
  margin-bottom: 2px;
}

.placeholder-line {
  visibility: hidden;
}

/* 버튼 스타일 (공지와 통일) */
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

.btn-primary-outline {
  color: #2563eb;
  border-color: #93c5fd;
  border-radius: 8px;
}

.btn-primary-outline:hover {
  background-color: #eff6ff;
  border-color: #60a5fa;
  color: #1d4ed8;
}

/* ✅ 페이지네이션 스타일 (공지와 동일 컨셉) */
.pagination-wrapper {
  font-size: 0.875rem;
}

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

.exam-title-btn {
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  color: inherit;
  font: inherit;
  text-align: left;
  width: 100%;
  cursor: pointer;
}

.exam-title-btn:hover {
  font-weight: bold;
}

</style>
