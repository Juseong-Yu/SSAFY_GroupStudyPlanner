<!-- src/views/studies/exams/ExamTakePage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4">
      <!-- 상단 헤더 영역 -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h2 class="fw-bold mb-1">
            시험 응시
            <span v-if="examTitle"> - {{ examTitle }}</span>
          </h2>
          <p class="text-muted small mb-0">
            스터디 ID: {{ studyId }} / 시험 ID: {{ examId }}
          </p>
          <p v-if="examDueAtText" class="text-muted small mb-0">
            마감 시간: {{ examDueAtText }}
          </p>
        </div>
        <!-- 타이머 자리 (나중에 실제 타이머로 교체 가능) -->
        <div class="text-end">
          <span class="badge bg-primary-subtle text-primary px-3 py-2">
            남은 시간: {{ dummyTimeText }}
          </span>
        </div>
      </div>

      <!-- 로딩 / 에러 / 본문 -->
      <div v-if="loading" class="text-center text-muted py-5">
        시험 정보를 불러오는 중입니다...
      </div>

      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <div v-else-if="!currentProblem">
        <div class="alert alert-warning">
          표시할 문제가 없습니다.
        </div>
      </div>

      <div v-else class="row g-3">
        <!-- 왼쪽: 문제 풀이 영역 -->
        <div class="col-12 col-lg-9">
          <ProblemView
            :problem="currentProblem"
            :currentIndex="currentIndex"
            :total="problems.length"
            v-model="answers[currentProblem.id]"
            @goNext="goNext"
            @goPrev="goPrev"
          />
        </div>

        <!-- 오른쪽: 문제 번호 + 제출 버튼 -->
        <div class="col-12 col-lg-3">
          <QuestionList
            :problems="problems"
            :answers="answers"
            :currentIndex="currentIndex"
            :submitting="submitting"
            @select="selectProblem"
            @submitExam="submitExam"
          />
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import AppShell from '@/layouts/AppShell.vue'
import QuestionList from './QuestionList.vue'
import ProblemView from './ProblemView.vue'
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

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
  created_at: string
  author: {
    id: number
    username: string
    email: string
  }
  questions: BackendExamQuestion[]
}

// 프론트에서 쓰는 문제 타입
type ProblemType = 'multiple' | 'short' | 'essay'

interface Problem {
  id: number
  number: number          // = order
  type: ProblemType
  question: string
  choices?: string[]      // 객관식일 경우만
}

// 라우터에서 studyId, examId 가져오기
const route = useRoute()
const router = useRouter()

const studyId = computed(() => route.params.studyId as string)
const examId = computed(() => route.params.examId as string)

// 시험 메타 정보
const examTitle = ref<string>('')
const examDueAtText = ref<string>('')

// 상태
const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)

const problems = ref<Problem[]>([])
const currentIndex = ref(0)
const answers = ref<Record<number, string | number | null>>({})

// 더미 타이머 텍스트 (나중에 실제 로직으로 교체 가능)
const dummyTimeText = computed(() => '00:30:00')

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

// ✅ exam_detail 사용해서 시험 + 문제 가져오기
async function fetchExamDetail() {
  try {
    loading.value = true
    error.value = null

    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const res = await axios.get<BackendExamDetail>(
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
    examDueAtText.value = formatKoreanDateTime(exam.due_at)

    // 백엔드 questions -> 프론트 Problem[] 변환
    problems.value = exam.questions
      .sort((a, b) => a.order - b.order)
      .map((q) => {
        // 현재 exam_detail 구조상 choices는 객관식 문제로 사용 가능
        const hasChoices = Array.isArray(q.choices) && q.choices.length > 0
        const type: ProblemType = hasChoices ? 'multiple' : 'short' // 필요하면 서술형으로 분리

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
async function submitExam() {
  if (!currentProblem.value || problems.value.length === 0) return

  const confirmMsg = '정말 시험을 제출할까요? 제출 후에는 답안을 수정할 수 없습니다.'
  const confirmed = window.confirm(confirmMsg)
  if (!confirmed) return

  try {
    submitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // TODO: 백엔드 submit API 스펙에 맞게 payload 조정 필요
    // 지금은 { question_id: answerValue } 형태로 보냄
    await axios.post(
      `${API_BASE}/studies/${studyId.value}/exams/${examId.value}/submit/`,
      {
        answers: answers.value,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      },
    )

    alert('시험이 정상적으로 제출되었습니다.')
    router.push({ name: 'StudyExams', params: { studyId: studyId.value } })
  } catch (e) {
    console.error(e)
    alert('시험 제출 중 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchExamDetail()
})
</script>
