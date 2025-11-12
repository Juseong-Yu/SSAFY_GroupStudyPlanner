<!-- src/views/studies/NoticeCreatePage.vue -->
<template>
  <AppShell>
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-xl-10 col-lg-11">
          <!-- 헤더 -->
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h3 class="mb-0 fw-bold">공지사항 작성</h3>
            <div class="d-flex align-items-center gap-2">
              <!-- <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="publishSwitch"
                  v-model="isPublished"
                />
                <label class="form-check-label" for="publishSwitch">
                  {{ isPublished ? '공개' : '임시저장' }}
                </label>
              </div> -->
              <RouterLink to="/studies" class="btn btn-outline-secondary">취소</RouterLink>
              <button class="btn btn-outline-primary" :disabled="submitting" @click="submitNotice">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" />
                {{ submitting ? '등록 중...' : '등록하기' }}
              </button>
            </div>
          </div>

          <!-- 제목 -->
          <div class="card shadow-sm border-0 mb-3">
            <div class="card-body">
              <input
                type="text"
                v-model.trim="title"
                class="form-control form-control-lg"
                placeholder="제목을 입력하세요"
              />
            </div>
          </div>

          <!-- 마크다운 에디터 -->
          <div class="card shadow-sm border-0">
            <div class="card-body">
              <MdEditor
                v-model="markdown"
                language="en-US"
                :preview="false"
                :no-upload-img="false"
                :toolbars-exclude="['save', 'github']"
                :style="{ height: '600px' }"
                @onUploadImg="handleUploadImg"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import axios from 'axios'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

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
      // TODO: 실제 업로드 URL로 교체
      const res = await axios.post('/api/uploads/images/', form, {
        headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      })
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

    // ✅ URLSearchParams 사용
    const params = new URLSearchParams()
    params.set('study_id', String(studyId))
    params.set('title', title.value.trim())
    params.set('content', markdown.value.trim())

    const response = await axios.post(`${API_BASE}/posts/create_notice/`, params, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

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
</style>
