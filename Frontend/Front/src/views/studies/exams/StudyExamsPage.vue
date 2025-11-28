<!-- src/views/studies/exams/StudyExamsPage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100" style="max-width: 1000px">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="fw-bold mb-0">시험 전체보기</h2>
          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="openCreateModal"
          >
            + 시험 생성
          </button>
        </div>

        <!-- 시험 리스트 -->
        <div class="card shadow-sm">
          <div class="card-body">
            <div
              v-if="loading"
              class="text-center text-muted py-4"
            >
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
                <div>
                  <div class="fw-semibold">{{ exam.title }}</div>
                  <div class="small text-muted">
                    마감: {{ formatDateTime(exam.due_at) }}
                  </div>
                </div>
                <span class="badge bg-secondary-subtle text-secondary small">
                  {{ exam.visibility_label }}
                </span>
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
  </AppShell>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'
import AppShell from '@/layouts/AppShell.vue'
import ExamCreateModal from './ExamCreateModal.vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const route = useRoute()
const studyId = Number(route.params.studyId)

interface ExamListItem {
  id: number
  title: string
  due_at: string | null
  visibility: 'public' | 'score_only' | 'private'
  visibility_label: string
}

const exams = ref<ExamListItem[]>([])
const loading = ref(false)
const showCreateModal = ref(false)

const openCreateModal = () => {
  showCreateModal.value = true
}

const formatDateTime = (iso: string | null) => {
  if (!iso) return '마감 없음'
  const d = new Date(iso)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
    d.getDate(),
  ).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(
    d.getMinutes(),
  ).padStart(2, '0')}`
}

const fetchExams = async () => {
  loading.value = true
  try {
    // GET이라도 네 규칙 맞춰서 ensureCsrf 호출해 둘게
    await ensureCsrf()
    const res = await axios.get(`${API_BASE}/studies/${studyId}/exams/`, {
      withCredentials: true,
    })
    exams.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchExams()
})
</script>
