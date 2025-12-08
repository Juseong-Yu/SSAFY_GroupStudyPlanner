<!-- src/views/studies/exams/components/QuestionList.vue -->
<template>
  <div class="card shadow-sm sticky-top" style="top: 88px">
    <div class="card-header fw-semibold d-flex justify-content-between align-items-center">
      <span>문제 목록</span>
      <span class="badge bg-secondary-subtle text-secondary small">
        {{ problems.length }}문제
      </span>
    </div>

    <!-- 문제 번호 리스트 -->
    <div class="card-body p-2" style="max-height: 60vh; overflow-y: auto;">
      <button
        v-for="(p, idx) in problems"
        :key="p.id"
        type="button"
        class="btn w-100 mb-2 text-start btn-sm"
        :class="buttonClass(p.id, idx)"
        @click="$emit('select', idx)"
      >
        <div class="d-flex justify-content-between align-items-center">
          <span>{{ p.number }}번</span>
          <small v-if="answers[p.id]" class="text-success fw-semibold">
            답변 완료
          </small>
          <small v-else class="text-muted">
            미답
          </small>
        </div>
      </button>
    </div>

    <!-- 제출 버튼 -->
    <div class="card-footer">
      <button
        type="button"
        class="btn btn-light-outline btn-primary-outline w-100"
        :disabled="submitting"
        @click="$emit('submitExam')"
      >
        <span v-if="submitting">제출 중...</span>
        <span v-else>시험 제출</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Problem {
  id: number
  number: number
  type: 'multiple' | 'short' | 'essay'
  question: string
  choices?: string[]
}

const props = defineProps<{
  problems: Problem[]
  answers: Record<number, string | number | null>
  currentIndex: number
  submitting: boolean
}>()

function buttonClass(problemId: number, idx: number) {
  // ✅ 현재 문제: 너무 파란 배경 대신, 은은한 강조용 커스텀 클래스
  if (idx === props.currentIndex) {
    return 'btn-current-question'
  }
  // ✅ 답변한 문제
  if (props.answers[problemId]) {
    return 'btn-outline-success'
  }
  // ✅ 아직 안 푼 문제
  return 'btn-outline-secondary'
}
</script>

<style scoped>
/* 현재 문제 버튼: 과하게 파랗지 않고, 살짝만 강조 */
.btn-current-question {
  background-color: #f9fafb;
  border: 1px solid #dbeafe;
  color: #1d4ed8;
  font-weight: 500;
}

.btn-current-question:hover {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

/* 파란 아웃라인 제출 버튼 (기본 .btn-light-outline + 이거 조합) */
.btn-primary-outline {
  color: #2563eb;
  border-color: #bfdbfe;
}

.btn-primary-outline:hover {
  color: #1d4ed8;
  border-color: #93c5fd;
  background-color: #eff6ff;
}

.btn-primary-outline:disabled {
  opacity: 0.6;
  pointer-events: none;
}
</style>
