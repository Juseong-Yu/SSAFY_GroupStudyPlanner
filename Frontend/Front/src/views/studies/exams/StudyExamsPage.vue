<!-- src/views/studies/exams/StudyExamsPage.vue -->
<template>
  <AppShell>
    <!-- ✅ 다른 스터디 페이지들과 동일한 레이아웃 패턴 적용 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper">
        <!-- 상단 헤더 -->
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="fw-bold mb-0">시험 전체보기</h2>

          <!-- 리더만 시험 생성 버튼 표시 -->
          <button
            v-if="isPrivileged"
            type="button"
            class="btn btn-light-outline btn-sm"
            @click="openCreateModal"
          >
            + 시험 생성
          </button>
        </div>

        <!-- 시험 리스트 카드 -->
        <div class="card shadow-sm">
          <div class="card-body">
            <div v-if="loading" class="text-center text-muted py-4">
              시험 목록 불러오는 중...
            </div>

            <div v-else-if="exams.length === 0" class="text-center text-muted py-4">
              아직 등록된 시험이 없습니다.
            </div>

            <ul v-else class="list-group list-group-flush">
              <li
                v-for="exam in exams"
                :key="exam.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <!-- 왼쪽: 제목 / 마감 / 뱃지들 -->
                <div>
                  <div class="fw-semibold">{{ exam.title }}</div>
                  <div class="small text-muted">
                    마감: {{ formatDateTime(exam.due_at) }}
                  </div>
                  <div class="mt-1 d-flex flex-wrap gap-2 small">
                    <!-- 공개 범위 뱃지 -->
                    <span class="badge bg-secondary-subtle text-secondary">
                      {{ exam.visibility_label }}
                    </span>

                    <!-- 응시 여부 뱃지 -->
                    <span
                      v-if="exam.has_taken"
                      class="badge bg-success-subtle text-success"
                    >
                      응시 완료
                    </span>
                    <span
                      v-else
                      class="badge bg-primary-subtle text-primary"
                    >
                      미응시
                    </span>
                  </div>
                </div>

                <!-- 오른쪽: 액션 버튼 -->
                <div class="text-end">
                  <!-- ✅ 리더 / admin: 시험 응시 + 결과 확인 -->
                  <template v-if="isPrivileged">
                    <div class="d-flex gap-2 justify-content-end">
                      <!-- 아직 응시 안 했으면: 시험 응시 버튼 노출 -->
                      <button
                        v-if="!exam.has_taken"
                        type="button"
                        class="btn btn-light-outline btn-sm"
                        @click="handleExamClick(exam)"
                      >
                        시험 응시
                      </button>

                      <!-- 항상 노출: 결과 확인 (미리보기 / 내 결과 확인 공통) -->
                      <button
                        type="button"
                        class="btn btn-primary-outline btn-sm"
                        @click="openResultModal(exam)"
                      >
                        결과 확인
                      </button>
                    </div>
                  </template>

                  <!-- ✅ 일반 멤버: 기존 동작 유지 -->
                  <template v-else>
                    <button
                      type="button"
                      class="btn btn-primary-outline btn-sm"
                      @click="handleExamClick(exam)"
                    >
                      {{ exam.has_taken ? '응시 내역 보기' : '시험 응시' }}
                    </button>
                  </template>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 시험 생성 모달 -->
    <ExamCreateModal
      v-if="showCreateModal"
      :study-id="studyId"
      @close="showCreateModal = false"
    />

    <!-- 응시 결과 모달 -->
    <ExamResultModal
      v-if="showResultModal"
      :visible="showResultModal"
      :my-result="myResult"
      :scoreboard="scoreboard"
      :all-results-detail="allResultsDetail"
      :can-see-own-detail="canSeeOwnDetail"
      :can-see-scoreboard="canSeeScoreboard"
      :can-see-others-detail="canSeeOthersDetail"
      :is-leader="isPrivileged"
      :problems="selectedExamProblems"
      :exam-title="selectedExamTitle"
      @close="showResultModal = false"
    />
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
import { useUserStore } from '@/stores/user' // ✅ admin 정보용 (프로젝트에 맞게 조정)

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

// 라우트에서 studyId 가져오기
const studyId = Number(route.params.studyId)

type VisibilityType = 'public' | 'score_only' | 'private'

interface ExamListItem {
  id: number
  title: string
  due_at: string | null
  visibility: VisibilityType
  visibility_label: string
  has_taken: boolean
}

// exam_detail / my_result 에서 내려올 문제 타입 (필요 시 조정)
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

// ✅ 관리자 여부 (프로젝트 User 모델에 맞게 필드 조정 가능)
const isAdmin = computed(() => studyRoleStore.isAdmin(String(studyId))
)

// ✅ 리더이거나 admin인 경우: 시험 응시 + 결과 확인 버튼 모두 노출
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
  // score_only / private -> 멤버는 전체 점수표 X
  return false
})

const canSeeOthersDetail = computed(() => {
  // 리더 / admin 은 항상 다른 사람 상세 결과까지 볼 수 있음
  return isPrivileged.value
})

// ===== 공통 유틸 =====
const openCreateModal = () => {
  showCreateModal.value = true
}

const formatDateTime = (iso: string | null) => {
  if (!iso) return '마감 없음'
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

// 공개 범위 → 라벨 매핑 (백엔드에서 visibility_label 안 내려줘도 대응)
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
      due_at: exam.due_at,
      visibility: exam.visibility as VisibilityType,
      visibility_label: exam.visibility_label
        ? exam.visibility_label
        : visibilityLabelMap[exam.visibility as VisibilityType] ?? '전체 공개',
      has_taken: Boolean(exam.has_taken),
    }))
  } finally {
    loading.value = false
  }
}

// ===== 버튼 클릭: 응시 / 응시 내역 보기 =====
const handleExamClick = (exam: ExamListItem) => {
  if (!exam.has_taken) {
    // 아직 응시 안 했으면 응시 페이지로 이동
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
      console.log(res.data)
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

    // 문제 정보가 같이 온다고 가정 (없으면 별도 exam_detail 호출로 대체 가능)
    selectedExamProblems.value =
      data.questions?.map((q) => ({
        id: q.id,
        order: q.order,
        text: q.text,
        choices: q.choices,
      })) ?? []

    showResultModal.value = true
  } catch (err : any) {
    console.error(err)
    alert(err.response.data.detail)
  }
}

onMounted(() => {
  fetchExams()
})
</script>

<style scoped>
.study-page-wrapper {
  width: 100%;
  max-width: 1300px;        /* 전체 폭 중앙 정렬 */
  padding-left: 1rem;     /* 항상 좌우 여백 유지 */
  padding-right: 1rem;
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
</style>
