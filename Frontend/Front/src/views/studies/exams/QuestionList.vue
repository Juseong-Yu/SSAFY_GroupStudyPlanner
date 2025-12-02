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
        class="btn btn-danger w-100"
        :disabled="submitting"
        @click="$emit('submitExam')"
      >
        <span v-if="submitting">제출 중...</span>
        <span v-else>시험 제출하기</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

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
  if (idx === props.currentIndex) {
    return 'btn-primary text-white'
  }
  if (props.answers[problemId]) {
    return 'btn-outline-success'
  }
  return 'btn-outline-secondary'
}
</script>
