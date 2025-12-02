<!-- src/views/studies/exams/ExamResultModal.vue -->
<template>
  <!-- 백드롭 + 모달 -->
  <div
    v-if="visible"
    class="modal fade show"
    tabindex="-1"
    role="dialog"
    style="display: block; background: rgba(0, 0, 0, 0.4);"
    aria-modal="true"
  >
    <div class="modal-dialog modal-xl modal-dialog-centered" role="document">
      <div class="modal-content">
        <!-- 헤더 -->
        <div class="modal-header">
          <h5 class="modal-title">
            시험 결과
            <span v-if="examTitleToShow" class="text-muted small ms-2">
              ({{ examTitleToShow }})
            </span>
          </h5>
          <button
            type="button"
            class="btn-close"
            aria-label="Close"
            @click="emitClose"
          ></button>
        </div>

        <!-- 바디 -->
        <div class="modal-body">
          <!-- 상단 요약 -->
          <div class="mb-3">
            <div class="d-flex flex-wrap align-items-center gap-2">
              <span class="fw-semibold">
                내 역할:
                <span v-if="isLeader">스터디 리더</span>
                <span v-else>일반 멤버</span>
              </span>

              <span
                v-if="isLeader"
                class="badge bg-primary-subtle text-primary"
              >
                전체 결과 열람 가능
              </span>
            </div>

            <p v-if="myResult" class="text-muted small mb-0">
              내 점수:
              <strong>{{ myResult.score.toFixed(1) }}</strong> 점
              ({{ myResult.correct_count }} / {{ myResult.total_count }}문제 정답)
              <span v-if="myResult.submitted_at">
                · 제출 시각: {{ formatDateTime(myResult.submitted_at) }}
              </span>
            </p>
          </div>

          <hr />

          <!-- 1) 내 문항별 결과 -->
          <section v-if="canSeeOwnDetail && myResult">
            <h6 class="fw-bold mb-2">내 문항별 결과</h6>

            <div
              v-for="item in myDetailedList"
              :key="item.problem.id"
              class="border rounded-3 p-3 mb-2"
            >
              <div class="d-flex justify-content-between align-items-center mb-1">
                <div>
                  <span class="fw-semibold">
                    {{ item.displayNumber }}번
                  </span>
                </div>
                <span
                  class="badge"
                  :class="item.isCorrect ? 'bg-success' : 'bg-danger'"
                >
                  {{ item.isCorrect ? '정답' : '오답' }}
                </span>
              </div>

              <p class="mb-2">
                {{ item.problem.text }}
              </p>

              <!-- 객관식 선택지 리스트 -->
              <ul
                v-if="item.problem.choices && item.problem.choices.length"
                class="list-unstyled small mb-2"
              >
                <li
                  v-for="(choice, idx) in item.problem.choices"
                  :key="idx"
                  class="d-flex align-items-center mb-1"
                >
                  <span
                    class="me-2 badge rounded-pill"
                    :class="choiceBadgeClass(idx, item.selectedIndex, item.correctIndex)"
                  >
                    {{ choiceLabel(idx) }}
                  </span>
                  <span>{{ choice }}</span>
                </li>
              </ul>

              <p class="small text-muted mb-0" v-if="item.userChoiceText !== null">
                내 답: {{ item.userChoiceText }}
              </p>
              <p class="small text-muted mb-0" v-if="item.correctChoiceText !== null">
                정답: {{ item.correctChoiceText }}
              </p>
            </div>
          </section>

          <!-- 2) 결과 비공개 안내 -->
          <section v-if="!canSeeOwnDetail && !canSeeScoreboard && !canSeeOthersDetail">
            <p class="mb-0">
              이 시험은 결과가 비공개로 설정되어 있습니다. 제출만 완료되었습니다.
            </p>
          </section>

          <!-- 3) 전체 점수표 -->
          <section v-if="canSeeScoreboard && scoreboard.length">
            <hr />
            <h6 class="fw-bold mb-2 d-flex align-items-center">
              전체 점수
              <span
                v-if="isLeader"
                class="badge bg-primary-subtle text-primary ms-2"
              >
                리더 권한
              </span>
            </h6>

            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th>이름</th>
                    <th class="text-end">점수</th>
                    <th class="text-end">정답 수</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in scoreboard"
                    :key="row.result_id"
                    :class="{
                      'table-active': row.user?.id === myResult?.user?.id,
                    }"
                    @click="handleSelectOtherResult(row)"
                    style="cursor: pointer"
                  >
                    <td>
                      {{ row.user?.username || '알 수 없음' }}
                      <span
                        v-if="row.user?.id === myResult?.user?.id"
                        class="badge bg-secondary-subtle text-secondary ms-1"
                      >
                        나
                      </span>
                    </td>
                    <td class="text-end">
                      {{ row.score.toFixed(1) }}
                    </td>
                    <td class="text-end">
                      {{ row.correct_count }}/{{ row.total_count }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <!-- 4) 리더 전용: 다른 사람 문항별 상세 -->
          <section v-if="canSeeOthersDetail && otherDetailedList.length">
            <hr />
            <h6 class="fw-bold mb-2">응시자별 문항 상세 (리더 전용)</h6>

            <div class="mb-3">
              <label class="form-label small mb-1">응시자 선택</label>
              <select
                class="form-select form-select-sm"
                v-model="selectedOtherResultId"
              >
                <option
                  v-for="r in allResultsDetail"
                  :key="r.result_id"
                  :value="r.result_id"
                >
                  {{ r.user?.username || '알 수 없음' }} ({{ r.score.toFixed(1) }}점)
                </option>
              </select>
            </div>

            <div
              v-for="item in otherDetailedList"
              :key="item.problem.id"
              class="border rounded-3 p-3 mb-2"
            >
              <div class="d-flex justify-content-between align-items-center mb-1">
                <div>
                  <span class="fw-semibold">
                    {{ item.displayNumber }}번
                  </span>
                </div>
                <span
                  class="badge"
                  :class="item.isCorrect ? 'bg-success' : 'bg-danger'"
                >
                  {{ item.isCorrect ? '정답' : '오답' }}
                </span>
              </div>

              <p class="mb-2">
                {{ item.problem.text }}
              </p>

              <ul
                v-if="item.problem.choices && item.problem.choices.length"
                class="list-unstyled small mb-2"
              >
                <li
                  v-for="(choice, idx) in item.problem.choices"
                  :key="idx"
                  class="d-flex align-items-center mb-1"
                >
                  <span
                    class="me-2 badge rounded-pill"
                    :class="choiceBadgeClass(idx, item.selectedIndex, item.correctIndex)"
                  >
                    {{ choiceLabel(idx) }}
                  </span>
                  <span>{{ choice }}</span>
                </li>
              </ul>

              <p class="small text-muted mb-0" v-if="item.userChoiceText !== null">
                선택한 답: {{ item.userChoiceText }}
              </p>
              <p class="small text-muted mb-0" v-if="item.correctChoiceText !== null">
                정답: {{ item.correctChoiceText }}
              </p>
            </div>
          </section>
        </div>

        <!-- 푸터 -->
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="emitClose">
            닫기
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="emitGoList"
          >
            시험 목록으로
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
/* 모달 body 안에서 스크롤이 너무 길어질 경우 대비 (선택 사항) */
.modal-body {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}
</style>
