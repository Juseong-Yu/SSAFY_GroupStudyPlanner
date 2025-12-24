<!-- src/views/studies/exams/components/ExamCreateModal.vue (예시 경로) -->
<template>
  <!-- 백드롭 -->
  <div class="modal-backdrop fade show"></div>

  <!-- 모달 -->
  <div class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" ref="modalRootRef">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">
        <!-- 헤더 -->
        <div class="modal-header">
          <h5 class="modal-title">시험 생성</h5>
          <button type="button" class="btn-close" @click="onClose"></button>
        </div>

        <!-- 본문 -->
        <div class="modal-body">
          <!-- 탭 -->
          <ul class="nav nav-tabs mb-3">
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: mode === 'manual' }"
                type="button"
                @click="mode = 'manual'"
              >
                직접 생성
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: mode === 'ai' }"
                type="button"
                @click="mode = 'ai'"
              >
                AI 생성
              </button>
            </li>
          </ul>

          <!-- 공통 필드 -->
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label">시험 제목</label>
              <input
                v-model="title"
                type="text"
                class="form-control"
                placeholder="예: 3주차 알고리즘 퀴즈"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">문제 수</label>
              <input v-model.number="questionCount" type="number" min="1" class="form-control" />
            </div>

            <div class="col-md-6">
              <label class="form-label">결과 공개 범위</label>
              <select v-model="visibility" class="form-select">
                <option value="public">모두에게 점수/문항 공개</option>
                <option value="score_only">내 점수만 공개</option>
                <option value="private">비공개 (리더만 확인)</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label">시작 일시 (선택)</label>
              <input v-model="startDate" type="datetime-local" class="form-control" />
              <div class="form-text">비워두면 생성 직후부터 응시할 수 있습니다.</div>
            </div>

            <div class="col-md-6">
              <label class="form-label">마감 일시 (선택)</label>
              <input v-model="dueDate" type="datetime-local" class="form-control" />
              <div class="form-text">비워두면 마감 시간 제한 없이 응시할 수 있습니다.</div>
            </div>
          </div>

          <!-- AI 생성 전용 영역 -->
          <div v-if="mode === 'ai'" class="mt-4">
            <h6 class="fw-semibold mb-2">AI 입력 데이터</h6>

            <div class="mb-3">
              <label class="form-label">참고 텍스트</label>
              <textarea
                v-model="aiText"
                class="form-control"
                rows="4"
                placeholder="AI가 문제를 만들 때 참고할 내용을 입력하세요."
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">파일 업로드 (선택)</label>
              <input
                ref="fileInputRef"
                type="file"
                class="form-control"
                accept=".txt,.docx"
                @change="onFileChange"
              />
              <div class="form-text">TXT, DOCX 파일만 업로드 가능</div>
            </div>
          </div>

          <div v-if="errorMessage" class="alert alert-danger mt-3 small">
            {{ errorMessage }}
          </div>
        </div>

        <!-- 푸터 -->
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm"
            :disabled="isSubmitting"
            @click="onClose"
          >
            취소
          </button>
          <button
            type="button"
            class="btn btn-primary btn-sm"
            :disabled="isSubmitting"
            @click="onSubmit"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
            다음으로
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Props {
  studyId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const router = useRouter()

const mode = ref<'manual' | 'ai'>('manual')
const title = ref('')
const questionCount = ref<number>(5)
const visibility = ref<'public' | 'score_only' | 'private'>('public')

// ✅ 시작/마감 일시는 datetime-local과 맞춰 string으로 관리
const startDate = ref<string>('') // "2025-12-10T13:00"
const dueDate = ref<string>('') // ""

const aiText = ref('')
const file = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const isSubmitting = ref(false)
const errorMessage = ref('')

const onClose = () => {
  if (!isSubmitting.value) {
    emit('close')
  }
}

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const selectedFile = target.files?.[0] ?? null

  if (!selectedFile) {
    file.value = null
    return
  }

  const allowedTypes = [
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]

  if (!allowedTypes.includes(selectedFile.type)) {
    errorMessage.value = 'TXT 또는 DOCX 파일만 업로드할 수 있습니다.'
    target.value = '' // 파일 선택 초기화
    file.value = null
    return
  }

  errorMessage.value = ''
  file.value = selectedFile
}

const validate = () => {
  if (!title.value.trim()) {
    errorMessage.value = '시험 제목을 입력해주세요.'
    return false
  }
  if (!questionCount.value || questionCount.value < 1) {
    errorMessage.value = '문제 수는 1개 이상이어야 합니다.'
    return false
  }

  // ✅ 시작/마감 둘 다 있으면 관계 검증
  if (startDate.value && dueDate.value) {
    const start = new Date(startDate.value).getTime()
    const due = new Date(dueDate.value).getTime()
    if (start >= due) {
      errorMessage.value = '시작 일시는 마감 일시보다 이전이어야 합니다.'
      return false
    }
  }

  errorMessage.value = ''
  return true
}

const onSubmit = async () => {
  if (!validate()) return

  // 1) 직접 생성 모드: 바로 에디터 페이지로 라우팅
  if (mode.value === 'manual') {
    router.push({
      name: 'ExamCreate', // 👉 라우터 name이 ExamCreatePage와 맞아야 함
      params: { studyId: props.studyId },
      query: {
        mode: 'manual',
        questionCount: questionCount.value,
        visibility: visibility.value,
        openDate: startDate.value || '',
        dueDate: dueDate.value || '',
        title: title.value.trim(),
      },
    })
    emit('close')
    return
  }

  // 2) AI 생성 모드: draft 생성 API 호출 → draftId 받으면 에디터 페이지로 이동
  try {
    isSubmitting.value = true
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken') || ''

    const formData = new FormData()
    formData.append('title', title.value.trim())
    formData.append('question_count', String(questionCount.value))
    formData.append('visibility', visibility.value)

    // ✅ 시작/마감 시간을 서버와 맞는 ISO 형식으로 전송
    if (startDate.value) {
      formData.append('start_at', new Date(startDate.value).toISOString())
    }
    if (dueDate.value) {
      formData.append('due_at', new Date(dueDate.value).toISOString())
    }

    if (aiText.value.trim()) {
      formData.append('context_text', aiText.value.trim())
    }
    if (file.value) {
      formData.append('context_file', file.value)
    }

    const res = await client.post(
      `${API_BASE}/studies/${props.studyId}/exams/ai-generate/`,
      formData,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
        },
      },
    )

    const draftId = res.data.draft_id as number

    router.push({
      name: 'ExamCreate',
      params: { studyId: props.studyId },
      query: {
        mode: 'ai',
        draftId,
        questionCount: questionCount.value,
        visibility: visibility.value,
        openDate: startDate.value || '',
        dueDate: dueDate.value || '',
        title: title.value.trim(),
      },
    })
    emit('close')
  } catch (error) {
    console.error(error)
    errorMessage.value = 'AI 문제 생성 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* 필요시 모달 커스텀 스타일 추가 가능 */
</style>
