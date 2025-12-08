<!-- src/views/studies/exams/ExamResultModal.vue -->
<template>
  <!-- 백드롭 + 모달 -->
  <div v-if="visible" class="modal fade show exam-result-modal" tabindex="-1" role="dialog" aria-modal="true">
    <div class="modal-dialog modal-xl modal-dialog-centered" role="document">
      <div class="modal-content">
        <!-- 헤더 -->
        <div class="modal-header border-0 pb-0">
          <div>
            <p class="text-uppercase text-muted small mb-1 fw-semibold section-label">
              시험 결과
            </p>
            <h5 class="modal-title fw-bold d-flex align-items-center mb-0">
              <span>{{ examTitleToShow || '시험' }}</span>
              <span v-if="isLeader" class="badge bg-primary-subtle text-primary ms-2">
                리더 권한
              </span>
            </h5>
          </div>

          <button type="button" class="btn-close" aria-label="Close" @click="emitClose"></button>
        </div>

        <!-- 바디 -->
        <div class="modal-body">
          <!-- 상단 요약 카드 -->
          <div class="summary-card mb-3">
            <div class="row g-3 align-items-center">
              <div class="col-md-4 border-md-end">
                <div class="d-flex flex-column gap-1">
                  <span class="text-muted small">내 역할</span>
                  <div class="d-flex align-items-center gap-2">
                    <span class="fw-semibold">
                      <span v-if="isLeader">스터디 리더</span>
                      <span v-else>일반 멤버</span>
                    </span>
                    <span v-if="isLeader" class="badge bg-primary-subtle text-primary">
                      전체 결과 열람 가능
                    </span>
                  </div>
                </div>
              </div>

              <div class="col-md-4 border-md-end">
                <div v-if="myResult" class="d-flex flex-column gap-1">
                  <span class="text-muted small">내 점수</span>
                  <div class="d-flex align-items-baseline gap-2">
                    <span class="fs-4 fw-bold">
                      {{ myResult.score.toFixed(1) }}
                    </span>
                    <span class="text-muted small">
                      ({{ myResult.correct_count }} / {{ myResult.total_count }}문제)
                    </span>
                  </div>
                  <span v-if="myResult.submitted_at" class="text-muted extra-small">
                    제출 시각 · {{ formatDateTime(myResult.submitted_at) }}
                  </span>
                </div>

                <div v-else class="text-muted small">
                  아직 제출된 결과가 없습니다.
                </div>
              </div>

              <div class="col-md-4">
                <div class="d-flex flex-column gap-1">
                  <span class="text-muted small">공개 범위</span>
                  <div class="d-flex flex-wrap gap-1">
                    <span v-if="canSeeOwnDetail" class="badge rounded-pill bg-success-subtle text-success">
                      내 문항별 결과
                    </span>
                    <span v-if="canSeeScoreboard" class="badge rounded-pill bg-primary-subtle text-primary">
                      전체 점수표
                    </span>
                    <span v-if="canSeeOthersDetail" class="badge rounded-pill bg-purple-subtle text-purple">
                      응시자 상세
                    </span>
                    <span v-if="!canSeeOwnDetail && !canSeeScoreboard && !canSeeOthersDetail"
                      class="badge rounded-pill bg-secondary-subtle text-secondary">
                      결과 비공개
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 1) 내 문항별 결과 -->
          <section v-if="canSeeOwnDetail && myResult">
            <div class="section-header d-flex justify-content-between align-items-center mb-2">
              <h6 class="fw-bold mb-0">
                내 문항별 결과
              </h6>
              <span class="text-muted extra-small">
                정답은 초록, 내가 선택한 오답은 빨강으로 표시됩니다.
              </span>
            </div>

            <div v-for="item in myDetailedList" :key="item.problem.id" class="question-card mb-2">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center gap-2">
                  <span class="question-number-pill">
                    {{ item.displayNumber }}
                  </span>
                  <span class="text-muted extra-small">문항</span>
                </div>
                <span class="badge score-badge"
                  :class="item.isCorrect ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
                  {{ item.isCorrect ? '정답' : '오답' }}
                </span>
              </div>

              <p class="mb-2 fw-semibold">
                {{ item.problem.text }}
              </p>

              <!-- 객관식 선택지 리스트 -->
              <ul v-if="item.problem.choices && item.problem.choices.length" class="list-unstyled small mb-2">
                <li v-for="(choice, idx) in item.problem.choices" :key="idx"
                  class="d-flex align-items-center mb-1 choice-row">
                  <span class="me-2 badge rounded-pill choice-pill"
                    :class="choiceBadgeClass(idx, item.selectedIndex, item.correctIndex)">
                    {{ choiceLabel(idx) }}
                  </span>
                  <span>{{ choice }}</span>
                </li>
              </ul>

              <div class="d-flex flex-wrap gap-2 small text-muted meta-row">
                <span v-if="item.userChoiceText !== null">
                  내 답: <strong>{{ item.userChoiceText }}</strong>
                </span>
                <span v-if="item.correctChoiceText !== null">
                  정답: <strong>{{ item.correctChoiceText }}</strong>
                </span>
              </div>
            </div>
          </section>

          <!-- 2) 결과 비공개 안내 -->
          <section v-if="!canSeeOwnDetail && !canSeeScoreboard && !canSeeOthersDetail">
            <div class="section-header mb-2">
              <h6 class="fw-bold mb-1">결과 비공개</h6>
            </div>
            <div class="question-card">
              <p class="mb-0 text-muted">
                이 시험은 결과가 비공개로 설정되어 있습니다. 제출만 완료되었습니다.
              </p>
            </div>
          </section>

          <!-- 3) 전체 점수표 -->
          <section v-if="canSeeScoreboard && scoreboard.length">
            <div class="section-header d-flex justify-content-between align-items-center mb-2 mt-4">
              <h6 class="fw-bold mb-0 d-flex align-items-center gap-2">
                전체 점수
                <span v-if="isLeader" class="badge bg-primary-subtle text-primary">
                  리더 권한
                </span>
              </h6>
              <span class="text-muted extra-small">
                행을 클릭하면 해당 응시자의 문항 상세로 이동합니다.
              </span>
            </div>

            <div class="card shadow-xs border-0 mb-0">
              <div class="table-responsive">
                <table class="table table-sm align-middle mb-0 score-table">
                  <thead>
                    <tr>
                      <th>이름</th>
                      <th class="text-end">점수</th>
                      <th class="text-end">정답 수</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in scoreboard" :key="row.result_id" :class="{
                      'table-active': row.user?.id === myResult?.user?.id,
                      'clickable-row': canSeeOthersDetail,
                    }" @click="handleSelectOtherResult(row)">
                      <td>
                        {{ row.user?.username || '알 수 없음' }}
                        <span v-if="row.user?.id === myResult?.user?.id"
                          class="badge bg-secondary-subtle text-secondary ms-1">
                          나
                        </span>
                      </td>
                      <td class="text-end fw-semibold">
                        {{ row.score.toFixed(1) }}
                      </td>
                      <td class="text-end text-muted">
                        {{ row.correct_count }}/{{ row.total_count }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <!-- 4) 리더 전용: 다른 사람 문항별 상세 -->
          <section v-if="canSeeOthersDetail && otherDetailedList.length">
            <div class="section-header d-flex justify-content-between align-items-center mb-2 mt-4">
              <h6 class="fw-bold mb-0">응시자별 문항 상세 (리더 전용)</h6>
            </div>

            <div class="mb-3 d-flex flex-column flex-md-row gap-2 align-items-md-center">
              <label class="form-label small mb-0 me-md-2">응시자 선택</label>
              <select class="form-select form-select-sm w-auto flex-grow-1 flex-md-grow-0"
                v-model="selectedOtherResultId">
                <option v-for="r in allResultsDetail" :key="r.result_id" :value="r.result_id">
                  {{ r.user?.username || '알 수 없음' }} ({{ r.score.toFixed(1) }}점)
                </option>
              </select>
            </div>

            <div v-for="item in otherDetailedList" :key="item.problem.id" class="question-card mb-2">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center gap-2">
                  <span class="question-number-pill">
                    {{ item.displayNumber }}
                  </span>
                  <span class="text-muted extra-small">문항</span>
                </div>
                <span class="badge score-badge"
                  :class="item.isCorrect ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
                  {{ item.isCorrect ? '정답' : '오답' }}
                </span>
              </div>

              <p class="mb-2 fw-semibold">
                {{ item.problem.text }}
              </p>

              <ul v-if="item.problem.choices && item.problem.choices.length" class="list-unstyled small mb-2">
                <li v-for="(choice, idx) in item.problem.choices" :key="idx"
                  class="d-flex align-items-center mb-1 choice-row">
                  <span class="me-2 badge rounded-pill choice-pill"
                    :class="choiceBadgeClass(idx, item.selectedIndex, item.correctIndex)">
                    {{ choiceLabel(idx) }}
                  </span>
                  <span>{{ choice }}</span>
                </li>
              </ul>

              <div class="d-flex flex-wrap gap-2 small text-muted meta-row">
                <span v-if="item.userChoiceText !== null">
                  선택한 답: <strong>{{ item.userChoiceText }}</strong>
                </span>
                <span v-if="item.correctChoiceText !== null">
                  정답: <strong>{{ item.correctChoiceText }}</strong>
                </span>
              </div>
            </div>
          </section>
        </div>

        <!-- 푸터 -->
        <div class="modal-footer border-0 pt-0">
          <button type="button" class="btn btn-light-outline" @click="emitClose">
            닫기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps, ref, watch } from 'vue'

type VisibilityType = 'public' | 'score_only' | 'private'

interface Problem {
  id: number
  order: number
  text: string
  choices: string[] | null
}

interface AnswerDetail {
  question_id: number
  order: number
  selected_index: number | null
  correct_index: number | null
  is_correct: boolean
}

interface MyResult {
  id: number
  user: {
    id: number
    username: string
  }
  score: number
  correct_count: number
  total_count: number
  submitted_at?: string
  answers: Record<number | string, AnswerDetail>
}

interface ScoreboardRow {
  result_id: number
  user: {
    id: number
    username: string
  }
  score: number
  correct_count: number
  total_count: number
}

interface ResultDetail {
  result_id: number
  user: {
    id: number
    username: string
  }
  score: number
  correct_count: number
  total_count: number
  answers: Record<number | string, AnswerDetail>
}

const props = defineProps<{
  visible: boolean
  myResult: MyResult | null
  scoreboard: ScoreboardRow[]
  allResultsDetail: ResultDetail[]
  canSeeOwnDetail: boolean
  canSeeScoreboard: boolean
  canSeeOthersDetail: boolean
  isLeader: boolean
  problems: Problem[]
  examTitle?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'goList'): void
}>()

const examTitleToShow = computed(() => props.examTitle ?? '')

// ===== 공통 유틸 =====
function formatDateTime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

function choiceLabel(idx: number): string {
  // 0,1,2,3 -> A,B,C,D
  return String.fromCharCode('A'.charCodeAt(0) + idx)
}

function choiceBadgeClass(
  idx: number,
  selectedIndex: number | null,
  correctIndex: number | null,
): string {
  if (correctIndex !== null && idx === correctIndex && idx === selectedIndex) {
    // 정답 + 사용자가 선택
    return 'bg-success text-white'
  }
  if (correctIndex !== null && idx === correctIndex) {
    // 정답
    return 'bg-success-subtle text-success'
  }
  if (selectedIndex !== null && idx === selectedIndex) {
    // 사용자가 선택했지만 오답
    return 'bg-danger-subtle text-danger'
  }
  return 'bg-light text-muted'
}

// ===== 내 문항별 상세 리스트 =====
const myDetailedList = computed(() => {
  if (!props.myResult) return []

  return props.problems.map((p, idx) => {
    const ans =
      props.myResult!.answers[p.id] ??
      props.myResult!.answers[String(p.id)]

    const selectedIndex = ans?.selected_index ?? null
    const correctIndex = ans?.correct_index ?? null
    const isCorrect = ans?.is_correct ?? false

    const userChoiceText =
      selectedIndex !== null &&
        p.choices &&
        p.choices[selectedIndex] !== undefined
        ? p.choices[selectedIndex]
        : null

    const correctChoiceText =
      correctIndex !== null &&
        p.choices &&
        p.choices[correctIndex] !== undefined
        ? p.choices[correctIndex]
        : null

    return {
      problem: p,
      displayNumber: p.order ?? idx + 1,
      selectedIndex,
      correctIndex,
      isCorrect,
      userChoiceText,
      correctChoiceText,
    }
  })
})

// ===== 리더용: 다른 응시자 상세 =====
const selectedOtherResultId = ref<number | null>(null)

watch(
  () => props.allResultsDetail,
  (list) => {
    if (list && list.length > 0) {
      selectedOtherResultId.value = list[0].result_id
    } else {
      selectedOtherResultId.value = null
    }
  },
  { immediate: true },
)

const selectedOtherResult = computed<ResultDetail | null>(() => {
  if (!selectedOtherResultId.value) return null
  return (
    props.allResultsDetail.find(
      (r) => r.result_id === selectedOtherResultId.value,
    ) ?? null
  )
})

const otherDetailedList = computed(() => {
  if (!props.canSeeOthersDetail || !selectedOtherResult.value) return []

  const r = selectedOtherResult.value

  return props.problems.map((p, idx) => {
    const ans = r.answers[p.id] ?? r.answers[String(p.id)]

    const selectedIndex = ans?.selected_index ?? null
    const correctIndex = ans?.correct_index ?? null
    const isCorrect = ans?.is_correct ?? false

    const userChoiceText =
      selectedIndex !== null &&
        p.choices &&
        p.choices[selectedIndex] !== undefined
        ? p.choices[selectedIndex]
        : null

    const correctChoiceText =
      correctIndex !== null &&
        p.choices &&
        p.choices[correctIndex] !== undefined
        ? p.choices[correctIndex]
        : null

    return {
      problem: p,
      displayNumber: p.order ?? idx + 1,
      selectedIndex,
      correctIndex,
      isCorrect,
      userChoiceText,
      correctChoiceText,
    }
  })
})

// scoreboard row 클릭 시, 해당 사람 상세로 이동 (리더일 때만 유효)
function handleSelectOtherResult(row: ScoreboardRow) {
  if (!props.canSeeOthersDetail) return
  selectedOtherResultId.value = row.result_id
}

function emitClose() {
  emit('close')
}

function emitGoList() {
  emit('goList')
}
</script>

<style scoped>
.exam-result-modal {
  display: block;
  background-color: rgba(15, 23, 42, 0.4);
  z-index: 1080;
}

.exam-result-modal .modal-dialog {
  max-width: 1100px;
}

.exam-result-modal .modal-content {
  border-radius: 16px;
  border: none;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
}

.modal-body {
  max-height: calc(100vh - 190px);
  overflow-y: auto;
  background-color: #f8fafc;
  padding-top: 1.25rem;
}

/* 상단 요약 카드 */
.summary-card {
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  border: 1px solid #e2e8f0;
}

.section-label {
  letter-spacing: 0.08em;
}

/* 섹션 헤더 */
.section-header {
  margin-top: 0.75rem;
}

.extra-small {
  font-size: 0.75rem;
}

/* 문항 카드 */
.question-card {
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 0.9rem 1rem;
}

.question-number-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  background-color: #eff4ff;
  color: #1d4ed8;
}

.score-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
}

/* 선택지 */
.choice-row {
  padding: 0.1rem 0;
}

.choice-pill {
  min-width: 26px;
  justify-content: center;
}

.meta-row span strong {
  font-weight: 600;
}

/* 테이블 */
.score-table thead th {
  border-bottom-width: 1px;
  border-color: #e2e8f0;
  font-size: 0.8rem;
  color: #64748b;
}

.score-table tbody td {
  font-size: 0.85rem;
}

.score-table tr.table-active {
  background-color: #e0edff;
}

.clickable-row {
  cursor: pointer;
}

/* 경계선 */
.border-md-end {
  border-right: none;
}

@media (min-width: 768px) {
  .border-md-end {
    border-right: 1px solid #e2e8f0;
  }
}

/* 푸터 버튼 */
.btn-light-outline {
  border: 1px solid #d0d7e2;
  background-color: #ffffff;
  color: #475569;
  border-radius: 8px;
  transition: 0.2s ease;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
}

.btn-light-outline:hover {
  background-color: #f1f5f9;
  border-color: #c5cedb;
}
</style>
