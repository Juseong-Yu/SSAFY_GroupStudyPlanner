<!-- src/views/studies/exams/components/ProblemView.vue -->
<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <!-- 상단 정보 -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0">
          {{ currentIndex + 1 }}번 문제
        </h5>
        <span class="text-muted small">
          (총 {{ total }}문제)
        </span>
      </div>

      <!-- 문제 내용 -->
      <p class="mb-4">
        {{ problem.question }}
      </p>

      <!-- 객관식 -->
      <div v-if="problem.type === 'multiple'">
        <div
          v-for="(choice, idx) in problem.choices"
          :key="idx"
          class="form-check mb-2"
        >
          <input
            class="form-check-input"
            type="radio"
            :name="'p-' + problem.id"
            :id="`p-${problem.id}-choice-${idx}`"
            :value="choice"
            v-model="model"
          />
          <label
            class="form-check-label"
            :for="`p-${problem.id}-choice-${idx}`"
          >
            {{ choice }}
          </label>
        </div>
      </div>

      <!-- 단답형 -->
      <div v-else-if="problem.type === 'short'">
        <input
          type="text"
          class="form-control"
          v-model="model"
          placeholder="정답을 입력하세요"
        />
      </div>

      <!-- 서술형 -->
      <div v-else-if="problem.type === 'essay'">
        <textarea
          class="form-control"
          rows="6"
          v-model="model"
          placeholder="내용을 입력하세요"
        ></textarea>
      </div>

      <!-- 이동 버튼 -->
      <div class="d-flex justify-content-between mt-4">
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="$emit('goPrev')"
          :disabled="currentIndex === 0"
        >
          이전 문제
        </button>

        <button
          type="button"
          class="btn btn-outline-primary"
          @click="$emit('goNext')"
          :disabled="currentIndex === total - 1"
        >
          다음 문제
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps } from 'vue'

interface Problem {
  id: number
  number: number
  type: 'multiple' | 'short' | 'essay'
  question: string
  choices?: string[]
}

const props = defineProps<{
  problem: Problem
  currentIndex: number
  total: number
  modelValue: string | number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number | null): void
  (e: 'goNext'): void
  (e: 'goPrev'): void
}>()

// v-model 대응용 computed
const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
</script>
