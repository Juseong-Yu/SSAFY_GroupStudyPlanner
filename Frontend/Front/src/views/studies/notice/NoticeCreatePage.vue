<!-- src/views/studies/NoticeCreatePage.vue -->
<template>
  <AppShell>
    <!-- ✅ StudyPage / MainPage와 동일한 레이아웃 패턴 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 notice-create-wrapper">
        <div class="row justify-content-center">
          <div class="col-xl-10 col-lg-11">
            <!-- 헤더 -->
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h3 class="mb-0 fw-bold">공지사항 작성</h3>
              <div class="d-flex align-items-center gap-2">
                <RouterLink :to="`/studies/${studyId}/notice`" class="btn btn-light-outline btn-sm">
                  취소
                </RouterLink>

                <button class="btn btn-light-outline btn-sm btn-primary-outline" :disabled="submitting"
                  @click="submitNotice">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2" />
                  {{ submitting ? '등록 중...' : '등록하기' }}
                </button>
              </div>

            </div>

            <!-- 제목 -->
            <div class="card shadow-sm border-0 mb-3">
              <div class="card-body">
                <input type="text" v-model.trim="title" class="form-control form-control-lg" placeholder="제목을 입력하세요" />
              </div>
            </div>

            <!-- 마크다운 에디터 -->
            <div class="card shadow-sm border-0">
              <div class="card-body">
                <MdEditor v-model="markdown" language="en-US" previewTheme="github" :preview="false"
                  :no-upload-img="false" :toolbars-exclude="['save', 'github']" :style="{ height: '600px' }"
                  @onUploadImg="handleUploadImg" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import client from '@/api/client'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const router = useRouter()
const route = useRoute()
const studyId = route.params.id

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// 상태
const title = ref('')
const submitting = ref(false)

// 에디터
const markdown = ref(``)
const toolbars = [
  'bold',
  'underline',
  'italic',
  'strikeThrough',
  'title',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  'code',
  'codeRow',
  'link',
  'image',
  'table',
  'preview',
  'pageFullscreen',
]

// 이미지 업로드 훅
const handleUploadImg = async (files: File[], callback: (urls: string[]) => void) => {
  try {
    await ensureCsrf()
    const csrfToken = getCookie('csrftoken')

    const urls: string[] = []
    for (const file of files) {
      const form = new FormData()
      form.append('image', file)
      const res = await client.post(
        `${API_BASE}/studies/${studyId}/posts/upload_img/`,
        form,
        {
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true,
        },
      )
      const url = res.data?.url
      if (!url) throw new Error('Upload response has no url')
      urls.push(url)
    }
    callback(urls)
  } catch (e) {
    console.error(e)
    alert('이미지 업로드 중 오류가 발생했어요.')
  }
}

// 공지사항 등록
const submitNotice = async () => {
  if (!title.value.trim()) return alert('제목을 입력하세요.')
  if (!markdown.value.trim()) return alert('내용을 입력하세요.')
  if (!studyId) return alert('스터디 ID가 없습니다.')

  try {
    submitting.value = true
    await ensureCsrf()
    const csrfToken = getCookie('csrftoken')

    const payload = {
      title: title.value.trim(),
      content: markdown.value.trim(),
    }

    const response = await client.post(
      `${API_BASE}/studies/${studyId}/posts/notice_create/`,
      payload,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      },
    )

    console.log('📢 공지 등록 완료:', response.data)
    alert('공지사항이 등록되었습니다!')
    router.push(`/studies/${studyId}/notice`)
  } catch (error) {
    console.error(error)
    alert('공지사항 등록 중 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.card {
  border-radius: 1rem;
}

/* ✅ StudyPage / NoticePage와 맞춘 레이아웃 래퍼 */
.notice-create-wrapper {
  width: 100%;
  max-width: 1300px;
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}

/* 모바일에서는 padding 살짝 줄이기 */
@media (max-width: 768px) {
  .notice-create-wrapper {
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

/* 기본 라이트 아웃라인 버튼 */
.btn-light-outline {
  border: 1px solid #d0d7e2;
  background-color: #ffffff;
  color: #475569;
  border-radius: 8px;
  transition: 0.2s ease;
  padding: 0.375rem 0.75rem; /* btn-sm 크기와 유사 */
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
}

/* hover */
.btn-light-outline:hover {
  background-color: #f1f5f9;
  border-color: #c5cedb;
  color: #334155;
}

/* disabled */
.btn-light-outline:disabled,
.btn-light-outline.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 등록하기 버튼만 약한 파란 강조 */
.btn-primary-outline {
  color: #2563eb;
  border-color: #93c5fd;
}

.btn-primary-outline:hover {
  background-color: #eff6ff;
  border-color: #60a5fa;
  color: #1d4ed8;
}

</style>
