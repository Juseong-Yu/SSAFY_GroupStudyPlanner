<!-- src/views/studies/exams/ExamTakePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper">
        <!-- 상단 헤더 카드 -->
        <div class="card shadow-sm border-0 mb-3">
          <div class="card-body py-3">
            <div class="exam-header d-flex justify-content-between align-items-center flex-wrap gap-3">
              <div>
                <h2 class="fw-bold mb-1">
                  <span v-if="examTitle">{{ examTitle }}</span>
                </h2>

                <!-- ⬇️ ID 라인 삭제하고, 메타 정보 줄 추가 -->
                <div class="d-flex flex-wrap align-items-center gap-2 small text-muted mt-1">
                  <span v-if="examDueAtText" class="badge exam-meta-badge">
                    마감 · {{ examDueAtText }}
                  </span>

                  <span v-if="problems.length" class="text-muted">
                    총 {{ problems.length }}문항
                  </span>
                </div>
              </div>

              <!-- 타이머 영역 -->
              <div class="timer-box text-end ms-auto">
                <div class="text-muted small mb-1">남은 시간</div>
                <div :class="['badge px-3 py-2 fs-6 timer-badge', timerClass]">
                  {{ timeLeftText }}
                </div>

              </div>
            </div>
          </div>
        </div>


        <!-- 본문 카드 (로딩/에러/문제 표시) -->
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <!-- 로딩 -->
            <div v-if="loading" class="text-center text-muted py-5">
              시험 정보를 불러오는 중입니다...
            </div>

            <!-- 에러 -->
            <div v-else-if="error">
              <div class="alert alert-danger mb-0">
                {{ error }}
              </div>
            </div>

            <!-- 문제 없음 -->
            <div v-else-if="!currentProblem">
              <div class="alert alert-warning mb-0">
                표시할 문제가 없습니다.
              </div>
            </div>

            <!-- 문제/번호 영역 -->
            <div v-else class="row g-4 align-items-start">
              <!-- 왼쪽: 문제 풀이 -->
              <div class="col-12 col-lg-9">
                <ProblemView :problem="currentProblem" :currentIndex="currentIndex" :total="problems.length"
                  v-model="answers[currentProblem.id]" @goNext="goNext" @goPrev="goPrev" />
              </div>

              <!-- 오른쪽: 문제 번호 + 제출 -->
              <div class="col-12 col-lg-3">
                <div class="exam-sidebar">
                  <QuestionList :problems="problems" :answers="answers" :currentIndex="currentIndex"
                    :submitting="submitting" @select="selectProblem" @submitExam="submitExam()" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'

import AppShell from '@/layouts/AppShell.vue'
import QuestionList from '@/views/studies/exams/components/QuestionList.vue'
import ProblemView from '@/views/studies/exams/components/ProblemView.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

interface BackendExamQuestion {
  id: number
  order: number
  text: string
  choices: string[] | null
  correct_index: number | null
}

interface BackendExamDetail {
  id: number
  title: string
  visibility: string
  due_at: string | null
  // 필요하면 open_at도 여기 추가 가능
  created_at: string
  author: {
    id: number
    username: string
    email: string
  }
  questions: BackendExamQuestion[]
}

type ProblemType = 'multiple' | 'short' | 'essay'

interface Problem {
  id: number
  number: number
  type: ProblemType
  question: string
  choices?: string[]
}

// 라우터에서 studyId, examId 가져오기
const route = useRoute()
const router = useRouter()

const studyId = computed(() => route.params.studyId as string)
const examId = computed(() => route.params.examId as string)

// 시험 메타 정보
const examTitle = ref<string>('')
const examDueAtText = ref<string>('')          // 화면용 포맷
const examDueAtRaw = ref<string | null>(null)  // 타이머용 원본 ISO

// 상태
const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)

const problems = ref<Problem[]>([])
const currentIndex = ref(0)
const answers = ref<Record<number, string | number | null>>({})

// ⭐ 타이머 상태
const remainingMs = ref<number | null>(null)
let timerId: number | null = null
let autoSubmitted = false  // 자동 제출이 한 번만 실행되도록 플래그

// 남은 시간 텍스트 (HH:MM:SS)
const timeLeftText = computed(() => {
  // 마감 시간 자체가 없으면 "제한 없음"
  if (!examDueAtRaw.value) {
    return '제한 없음'
  }

  if (remainingMs.value === null) {
    return '--:--:--'
  }

  const ms = Math.max(0, remainingMs.value)
  const totalSeconds = Math.floor(ms / 1000)

  const h = String(Math.floor(totalSeconds / 3600)).padStart(2, '0')
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0')
  const s = String(totalSeconds % 60).padStart(2, '0')

  return `${h}:${m}:${s}`
})

// 현재 문제
const currentProblem = computed<Problem | null>(() => {
  if (
    problems.value.length === 0 ||
    currentIndex.value < 0 ||
    currentIndex.value >= problems.value.length
  ) {
    return null
  }
  return problems.value[currentIndex.value]
})

// 문제 선택
function selectProblem(index: number) {
  if (index >= 0 && index < problems.value.length) {
    currentIndex.value = index
  }
}

// 이전/다음 이동
function goNext() {
  if (currentIndex.value < problems.value.length - 1) {
    currentIndex.value++
  }
}

function goPrev() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

// 날짜 포맷 (간단 버전)
function formatKoreanDateTime(isoString: string | null): string {
  if (!isoString) return ''
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime())) return isoString

  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')

  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

// 시간에 따라 색 변경
const timerClass = computed(() => {
  if (!examDueAtRaw.value || remainingMs.value === null) return ''

  const secondsLeft = Math.floor(remainingMs.value / 1000)

  // 30초 이하 → 빨간색 강조
  if (secondsLeft <= 30) return 'timer-danger'

  // 기본(중립)
  return 'timer-neutral'
})


// ⭐ 타이머 시작
function startTimer() {
  if (!examDueAtRaw.value) return

  // 혹시 기존 타이머 있으면 정리
  if (timerId !== null) {
    clearInterval(timerId)
    timerId = null
  }

  const update = () => {
    if (!examDueAtRaw.value) {
      remainingMs.value = null
      return
    }

    const now = Date.now()
    const due = new Date(examDueAtRaw.value).getTime()
    const diff = due - now

    remainingMs.value = diff

    // 시간이 다 되면 0으로 고정 + 타이머 종료 + 자동 제출
    if (diff <= 0) {
      remainingMs.value = 0
      if (timerId !== null) {
        clearInterval(timerId)
        timerId = null
      }

      // 이미 자동 제출했거나, 제출 중이면 또 보내지 않기
      if (!autoSubmitted && !submitting.value) {
        autoSubmitted = true
        // 약간의 여유를 주고 자동 제출 (네트워크/렌더 지연 대비)
        setTimeout(() => {
          submitExam(true)   // auto = true
        }, 500)
      }
    }
  }

  // 즉시 한 번 계산하고, 1초마다 갱신
  update()
  timerId = window.setInterval(update, 1000)
}

// 시험 + 문제 가져오기
async function fetchExamDetail() {
  try {
    loading.value = true
    error.value = null

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const res = await client.get<BackendExamDetail>(
      `${API_BASE}/studies/${studyId.value}/exams/${examId.value}/`,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      },
    )

    const exam = res.data
    examTitle.value = exam.title

    examDueAtRaw.value = exam.due_at
    examDueAtText.value = formatKoreanDateTime(exam.due_at)

    // 타이머 시작
    startTimer()

    // 백엔드 questions -> 프론트 Problem[] 변환
    problems.value = exam.questions
      .sort((a, b) => a.order - b.order)
      .map((q) => {
        const hasChoices = Array.isArray(q.choices) && q.choices.length > 0
        const type: ProblemType = hasChoices ? 'multiple' : 'short'

        const problem: Problem = {
          id: q.id,
          number: q.order,
          type,
          question: q.text,
        }

        if (hasChoices) {
          problem.choices = q.choices || []
        }

        return problem
      })

    // 아직 답변은 빈 상태
    answers.value = {}
    currentIndex.value = 0
  } catch (e) {
    console.error(e)
    error.value = '시험 정보를 불러오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// 시험 제출
async function submitExam(auto = false) {
  if (!currentProblem.value || problems.value.length === 0) return

  // ⛔ 수동 제출일 때만 "시간 종료" 막기
  if (!auto && examDueAtRaw.value && remainingMs.value !== null && remainingMs.value <= 0) {
    alert('시험 시간이 이미 종료되었습니다.')
    return
  }

  // ⛔ 수동 제출일 때만 confirm
  if (!auto) {
    const confirmMsg =
      '정말 시험을 제출할까요? 제출 후에는 답안을 수정할 수 없습니다.'
    const confirmed = window.confirm(confirmMsg)
    if (!confirmed) return
  }

  try {
    submitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.post(
      `${API_BASE}/studies/${studyId.value}/exams/${examId.value}/submit/`,
      {
        answers: answers.value,
        auto,  // ✅ 자동 제출 여부 플래그 같이 전송
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      },
    )

    if (auto) {
      alert('시험 시간이 종료되어 자동으로 제출되었습니다.')
    } else {
      alert('시험이 정상적으로 제출되었습니다.')
    }

    router.push({ name: 'StudyExams', params: { studyId: studyId.value } })
  } catch (e) {
    console.error(e)
    if (auto) {
      alert('시험 시간 종료 시 자동 제출 중 오류가 발생했습니다.')
    } else {
      alert('시험 제출 중 오류가 발생했습니다.')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchExamDetail()
})

onUnmounted(() => {
  if (timerId !== null) {
    clearInterval(timerId)
    timerId = null
  }
})
</script>

<style scoped>
.study-page-wrapper {
  width: 100%;
  max-width: 1300px;
  /* 전체 폭 중앙 정렬 */
  padding-left: 1rem;
  /* 항상 좌우 여백 유지 */
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

/* 상단 헤더 구분선 */
.exam-header {
  border-bottom: 1px solid var(--bs-border-color);
  padding-bottom: 0.5rem;
}

/* 메타 정보 배지 (마감 시간) */
.exam-meta-badge {
  background-color: #f3f4f6;
  /* 연한 회색 */
  color: #6b7280;
  /* 중간 회색 텍스트 */
  font-weight: 400;
  border-radius: 9999px;
  padding: 0.15rem 0.6rem;
}


/* 타이머 박스 */
.timer-box {
  min-width: 150px;
}

/* 오른쪽 사이드(문제 번호/제출 영역) */
.exam-sidebar {
  border-left: 1px solid var(--bs-border-color);
  padding-left: 1.25rem;
}

@media (max-width: 991.98px) {
  .exam-sidebar {
    border-left: none;
    border-top: 1px solid var(--bs-border-color);
    padding-left: 0;
    padding-top: 1.25rem;
    margin-top: 1.25rem;
  }
}

/* 기본 중립 스타일 */
.timer-badge.timer-neutral {
  background-color: #f3f4f6; /* 연한 회색 */
  color: #374151;           /* 진회색 */
  font-weight: 600;
  border-radius: 9999px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 30초 이하 → 빨간색 경고 */
.timer-badge.timer-danger {
  background-color: #fee2e2; /* 연한 빨간 배경 */
  color: #b91c1c;            /* 진한 빨간 텍스트 */
  font-weight: 700;
}

</style>
