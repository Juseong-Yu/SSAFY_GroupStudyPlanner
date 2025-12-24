<!-- src/views/studies/exams/ExamCreatePage.vue -->
<template>
  <AppShell>
    <!-- 바깥 컨테이너: 전체 가운데 정렬 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper d-flex justify-content-center">
        <!-- 중앙 정렬된 메인 + 오른쪽 네비 -->
        <div class="exam-layout d-flex justify-content-center gap-3 w-100">
          <!-- 🔹 가운데 문제 생성 영역 -->
          <div class="exam-main">
            <!-- 상단 헤더 -->
            <div class="d-flex justify-content-between align-items-center mb-3 w-100">
              <div>
                <h2 class="fw-bold mb-0">시험 문제 생성</h2>
                <p class="text-muted small mb-0">
                  {{ headerSubtitle }}
                </p>
              </div>
              <button
                type="button"
                class="btn btn-outline-secondary btn-sm"
                @click="goBack"
              >
                목록으로
              </button>
            </div>

            <!-- 시험 메타 정보 카드 -->
            <div class="card mb-4 shadow-sm">
              <div class="card-body small">
                <!-- 윗줄: 스터디 / 공개 범위 / 시작 / 마감 -->
                <div class="d-flex flex-wrap align-items-center gap-3 mb-3">
                  <!-- 스터디 정보 -->
                  <div class="d-flex align-items-center gap-2">
                    <span class="text-muted">스터디</span>
                    <span class="fw-semibold badge rounded-pill bg-primary-subtle text-primary">
                      #{{ studyId }}
                    </span>
                  </div>

                  <!-- 공개 범위: 선택 가능 -->
                  <div class="d-flex flex-column" style="min-width: 180px">
                    <label class="form-label small mb-1">공개 범위</label>
                    <select
                      v-model="selectedVisibility"
                      class="form-select form-select-sm"
                    >
                      <option value="public">모두 공개</option>
                      <option value="score_only">내 점수만 공개</option>
                      <option value="private">리더만 확인</option>
                    </select>
                  </div>

                  <!-- 시작 일시 (수정 가능) -->
                  <div class="d-flex flex-column" style="min-width: 220px">
                    <label class="form-label small mb-1">시작 일시</label>
                    <input
                      v-model="openAtInput"
                      type="datetime-local"
                      class="form-control form-control-sm"
                    />
                  </div>

                  <!-- 마감 일시 (수정 가능) -->
                  <div class="d-flex flex-column" style="min-width: 220px">
                    <label class="form-label small mb-1">마감 일시</label>
                    <input
                      v-model="dueAtInput"
                      type="datetime-local"
                      class="form-control form-control-sm"
                    />
                  </div>
                </div>

                <!-- 아랫줄: 시험 제목 (한 줄 전체 사용) -->
                <div>
                  <label class="form-label small mb-1">시험 제목</label>
                  <input
                    v-model="title"
                    type="text"
                    class="form-control form-control-sm"
                    placeholder="시험 제목을 입력하세요."
                  />
                </div>
              </div>
            </div>

            <!-- 문제 목록 헤더 -->
            <div
              class="d-flex justify-content-between align-items-center mb-3 pb-1 border-bottom"
            >
              <h5 class="fw-semibold mb-0">
                문제 목록
                <span class="badge rounded-pill bg-light text-muted ms-1">
                  {{ questions.length }}개
                </span>
              </h5>
              <div class="d-flex gap-2">
                <button
                  class="btn btn-outline-primary btn-sm"
                  type="button"
                  @click="addQuestion"
                >
                  + 문제 추가
                </button>
                <button
                  class="btn btn-outline-danger btn-sm"
                  type="button"
                  :disabled="questions.length <= 1"
                  @click="removeLastQuestion"
                >
                  마지막 문제 삭제
                </button>
              </div>
            </div>

            <!-- 🔹 문제 카드 리스트 -->
            <div class="mb-4">
              <!-- 문제 카드 반복 렌더링 -->
              <div
                v-for="(q, idx) in questions"
                :key="q.localId"
                :id="`question-${idx}`"
                class="card mb-3 shadow-sm question-card"
              >
                <div class="card-body">
                  <!-- 문제 헤더 -->
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <div class="d-flex align-items-center gap-2">
                      <span class="badge rounded-pill bg-primary-subtle text-primary">
                        Q{{ idx + 1 }}
                      </span>
                      <span class="text-muted small">문제 {{ idx + 1 }}</span>
                    </div>
                    <button
                      v-if="questions.length > 1"
                      type="button"
                      class="btn btn-outline-danger btn-sm"
                      @click="removeQuestion(idx)"
                    >
                      삭제
                    </button>
                  </div>

                  <!-- 문제 내용 -->
                  <div class="mb-3">
                    <label class="form-label small">문항 내용</label>
                    <textarea
                      v-model="q.text"
                      class="form-control"
                      rows="3"
                      placeholder="문제 내용을 입력하세요."
                    ></textarea>
                  </div>

                  <!-- 4지선다 보기 -->
                  <div>
                    <label class="form-label small d-flex justify-content-between">
                      보기 (4지선다)
                      <span class="text-muted small">정답 보기를 하나 선택하세요.</span>
                    </label>

                    <div
                      v-for="(choice, cIdx) in q.choices"
                      :key="cIdx"
                      class="input-group input-group-sm mb-1"
                    >
                      <span class="input-group-text">
                        <input
                          type="radio"
                          :name="'correct-' + q.localId"
                          :checked="q.correctIndex === cIdx"
                          @change="q.correctIndex = cIdx"
                        />
                      </span>
                      <input
                        v-model="q.choices[cIdx]"
                        type="text"
                        class="form-control"
                        :placeholder="`보기 ${cIdx + 1}`"
                      />
                    </div>

                    <div class="form-text">
                      보기 4개는 고정입니다. (객관식 4지선다)
                    </div>
                  </div>
                </div>
              </div>

              <!-- 🔹 리스트 맨 아래 문제 추가 버튼 (연한 회색 pill 스타일) -->
              <div class="d-flex justify-content-center mt-3">
                <button
                  class="btn btn-add-question"
                  type="button"
                  @click="addQuestion"
                >
                  <i class="bi bi-plus-lg me-1"></i> 문제 추가
                </button>
              </div>
            </div>

            <!-- 하단 버튼 -->
            <div class="d-flex justify-content-end gap-2">
              <button
                class="btn btn-outline-secondary"
                type="button"
                :disabled="isSubmitting"
                @click="goBack"
              >
                취소
              </button>
              <button
                class="btn btn-primary"
                type="button"
                :disabled="isSubmitting"
                @click="submitExam"
              >
                <span
                  v-if="isSubmitting"
                  class="spinner-border spinner-border-sm me-1"
                ></span>
                시험 생성 완료
              </button>
            </div>

            <div v-if="errorMessage" class="alert alert-danger mt-3 small">
              {{ errorMessage }}
            </div>
          </div>

          <!-- 🔹 문제 이동 패널: 오른쪽, 바로 옆 + sticky -->
          <aside class="exam-nav-wrapper d-none d-xl-block">
            <div class="position-sticky" style="top: 88px">
              <div class="card shadow-sm exam-nav-card">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <span class="fw-semibold small">문제 이동</span>
                  <span class="badge bg-light text-muted small">
                    {{ questions.length }}문항
                  </span>
                </div>
                <div class="list-group list-group-flush small">
                  <button
                    v-for="(q, idx) in questions"
                    :key="'nav-' + q.localId"
                    type="button"
                    class="list-group-item list-group-item-action exam-nav-item"
                    @click="scrollToQuestion(idx)"
                  >
                    <div class="d-flex align-items-center justify-content-between">
                      <div class="d-flex align-items-center gap-2">
                        <span
                          class="badge rounded-circle bg-primary-subtle text-primary nav-index-badge"
                        >
                          {{ idx + 1 }}
                        </span>
                        <span class="text-truncate">
                          문제 {{ idx + 1 }}
                        </span>
                      </div>
                    </div>
                  </button>
                </div>
                <div class="card-footer text-muted small">
                  번호를 클릭하면 해당 문제 위치로 이동합니다.
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import AppShell from '@/layouts/AppShell.vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Props {
  studyId: number
  mode: 'manual' | 'ai'
  questionCount: number
  visibility: 'public' | 'score_only' | 'private'
  dueDate: string | null          // datetime-local or ISO
  openDate: string | null         // datetime-local or ISO
  draftId: number | null
}

const props = defineProps<Props>()

interface Question {
  localId: number
  text: string
  choices: string[]
  correctIndex: number | null
}

const route = useRoute()
const router = useRouter()

const title = ref<string>((route.query.title as string) || '')
const questions = ref<Question[]>([])
const isSubmitting = ref(false)
const errorMessage = ref('')

let localIdCounter = 1

// 공개 범위: props에서 초기값 받고 수정 가능
const selectedVisibility = ref<Props['visibility']>(props.visibility)

// datetime-local용 로컬 문자열 (YYYY-MM-DDTHH:MM)
const openAtInput = ref<string>('')
const dueAtInput = ref<string>('')

// 설명 텍스트
const headerSubtitle = computed(() => {
  if (props.mode === 'ai') {
    return 'AI가 생성한 4지선다 문제를 검수하고 수정할 수 있습니다.'
  }
  return '4지선다 객관식 문제를 직접 작성합니다.'
})

/**
 * 문자열(ISO 또는 datetime-local)을 datetime-local input 포맷(YYYY-MM-DDTHH:MM)으로 변환
 */
const toLocalInputValue = (value: string | null): string => {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

/**
 * datetime-local 문자열을 ISO 문자열로 변환
 */
const toIsoOrNull = (localValue: string): string | null => {
  if (!localValue) return null
  const d = new Date(localValue)
  if (Number.isNaN(d.getTime())) return null
  return d.toISOString()
}

// 4지선다 기본 문제 생성
const createEmptyQuestion = (): Question => ({
  localId: localIdCounter++,
  text: '',
  choices: ['', '', '', ''],
  correctIndex: null,
})

const normalizeChoicesToFour = (choices: any): string[] => {
  const arr = Array.isArray(choices) ? choices.slice(0, 4) : []
  while (arr.length < 4) {
    arr.push('')
  }
  return arr
}

const addQuestion = () => {
  questions.value.push(createEmptyQuestion())
}

const removeLastQuestion = () => {
  if (questions.value.length > 1) {
    questions.value.pop()
  }
}

const removeQuestion = (index: number) => {
  if (questions.value.length <= 1) return
  questions.value.splice(index, 1)
}

const goBack = () => {
  router.push({
    name: 'StudyExams',
    params: { studyId: props.studyId },
  })
}

// ========================
// ⭐ AI Draft 불러오기
// ========================
const loadAiDraft = async () => {
  if (!props.draftId) return

  try {
    const res = await client.get(
      `${API_BASE}/studies/${props.studyId}/exams/ai-draft/${props.draftId}/`,
      {
        withCredentials: true,
      },
    )

    const data = res.data

    // exam_ai_draft_detail에서 내려주는 title 사용
    if (!title.value && data.title) {
      title.value = data.title
    }

    const draftQuestions = Array.isArray(data.questions) ? data.questions : []

    questions.value = draftQuestions.map((q: any) => ({
      localId: localIdCounter++,
      text: q.text ?? '',
      choices: normalizeChoicesToFour(q.choices),
      correctIndex:
        typeof q.correctIndex === 'number'
          ? Math.max(0, Math.min(3, q.correctIndex as number))
          : null,
    }))

    // 혹시라도 비어있으면 fallback
    if (questions.value.length === 0) {
      const count = props.questionCount || 5
      for (let i = 0; i < count; i++) {
        addQuestion()
      }
    }
  } catch (error) {
    console.error(error)
    errorMessage.value = 'AI 생성 결과를 불러오는 중 오류가 발생했습니다.'
    const count = props.questionCount || 5
    for (let i = 0; i < count; i++) {
      addQuestion()
    }
  }
}

const initQuestions = async () => {
  // 시작/마감 일시 초기값 설정
  openAtInput.value = toLocalInputValue(props.openDate)
  dueAtInput.value = toLocalInputValue(props.dueDate)

  if (props.mode === 'ai' && props.draftId) {
    await loadAiDraft()
  } else {
    const count = props.questionCount || 5
    for (let i = 0; i < count; i++) {
      addQuestion()
    }
  }
}

// 오른쪽 인덱스 클릭 시 스크롤 이동 (위에서 여백)
const scrollToQuestion = (idx: number) => {
  const el = document.getElementById(`question-${idx}`)
  if (!el) return

  const rect = el.getBoundingClientRect()
  const currentScroll = window.scrollY || window.pageYOffset
  const offset = 120 // 헤더 + 여백

  let target = currentScroll + rect.top - offset
  if (target < 0) target = 0

  window.scrollTo({
    top: target,
    behavior: 'smooth',
  })
}

// ========================
// 유효성 검사
// ========================
const validate = () => {
  if (!title.value.trim()) {
    errorMessage.value = '시험 제목을 입력해주세요.'
    return false
  }

  // ✅ 시작 / 마감은 "선택"이므로 필수 체크 제거
  let openDate: Date | null = null
  let dueDate: Date | null = null

  if (openAtInput.value) {
    const d = new Date(openAtInput.value)
    if (!Number.isNaN(d.getTime())) {
      openDate = d
    }
  }

  if (dueAtInput.value) {
    const d = new Date(dueAtInput.value)
    if (!Number.isNaN(d.getTime())) {
      dueDate = d
    }
  }

  // ✅ 둘 다 있을 때만 순서 검증
  if (openDate && dueDate && dueDate <= openDate) {
    errorMessage.value = '마감 일시는 시작 일시보다 뒤여야 합니다.'
    return false
  }

  if (questions.value.length === 0) {
    errorMessage.value = '최소 1개 이상의 문제가 필요합니다.'
    return false
  }

  for (const [idx, q] of questions.value.entries()) {
    if (!q.text.trim()) {
      errorMessage.value = `문제 ${idx + 1}의 내용을 입력해주세요.`
      return false
    }

    if (q.choices.length !== 4) {
      errorMessage.value = `문제 ${idx + 1}의 보기 개수가 올바르지 않습니다. (4개 필요)`
      return false
    }

    for (let i = 0; i < 4; i++) {
      if (!q.choices[i].trim()) {
        errorMessage.value = `문제 ${idx + 1}의 보기 ${i + 1} 내용을 입력해주세요.`
        return false
      }
    }

    if (
      q.correctIndex === null ||
      q.correctIndex < 0 ||
      q.correctIndex > 3
    ) {
      errorMessage.value = `문제 ${idx + 1}의 정답 보기를 선택해주세요.`
      return false
    }
  }

  errorMessage.value = ''
  return true
}


// ========================
// ⭐ 시험 생성 제출
// ========================
const submitExam = async () => {
  if (!validate()) return

  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const payload = {
      title: title.value.trim(),
      visibility: selectedVisibility.value,
      start_at: toIsoOrNull(openAtInput.value),
      due_at: toIsoOrNull(dueAtInput.value),
      questions: questions.value.map(q => ({
        text: q.text,
        choices: q.choices,
        // 백엔드는 snake_case: correct_index 기대
        correct_index: q.correctIndex,
      })),
      ai_draft_id: props.draftId,
    }

    await client.post(
      // ⬇️ 여기도 exams → exam 으로 수정
      `${API_BASE}/studies/${props.studyId}/exams/`,
      payload,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      },
    )

    router.push({
      name: 'StudyExams',
      params: { studyId: props.studyId },
    })
  } catch (error) {
    console.error(error)
    errorMessage.value = '시험 생성 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  initQuestions()
})
</script>

<style scoped>
/* StudyPage / SchedulePage와 동일한 반응형 너비 */
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

/* 중앙에 메인 + 오른쪽 네비를 나란히 */
.exam-layout {
  max-width: 1200px;
}

/* 가운데 문제 생성 영역 폭 */
.exam-main {
  max-width: 820px;
  width: 100%;
}

/* 문제 카드 */
.question-card {
  border-radius: 0.8rem;
}

/* 오른쪽 네비: 메인 바로 옆에 */
.exam-nav-wrapper {
  width: 260px;
  flex-shrink: 0;
}

.exam-nav-card {
  border-radius: 0.9rem;
}

.exam-nav-item {
  border: 0;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.exam-nav-item:hover {
  background-color: #f1f3f5;
}

.nav-index-badge {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

/* 문제 추가 버튼 (부드러운 연한 회색 pill 스타일) */
.btn-add-question {
  background: #f8f9fa; /* 매우 연한 회색 */
  color: #495057; /* 진한 회색 텍스트 */
  border: 1px solid #dee2e6;
  padding: 0.45rem 1.2rem;
  border-radius: 50px; /* pill 모양 */
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.15s ease-in-out;
}

.btn-add-question:hover {
  background: #e9ecef;
  border-color: #ced4da;
}
</style>
