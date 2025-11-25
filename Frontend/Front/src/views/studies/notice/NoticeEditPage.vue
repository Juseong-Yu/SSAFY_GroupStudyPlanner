<!-- src/views/studies/NoticeEditPage.vue -->
<template>
  <AppShell>
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-xl-10 col-lg-11">
          <!-- 헤더 -->
          <div class="d-flex align-items-center justify-content-between mb-3">
            <div>
              <h3 class="mb-0 fw-bold">공지사항 수정</h3>
              <p class="text-muted small mb-0" v-if="noticeId">
                notice #{{ noticeId }}
              </p>
            </div>
            <div class="d-flex align-items-center gap-2">
              <RouterLink
                :to="detailPath"
                class="btn btn-outline-secondary"
              >
                취소
              </RouterLink>
              <button
                class="btn btn-outline-primary"
                :disabled="submitting || isLoading"
                @click="submitNotice"
              >
                <span
                  v-if="submitting"
                  class="spinner-border spinner-border-sm me-2"
                />
                {{ submitting ? '수정 중...' : '수정하기' }}
              </button>
            </div>
          </div>

          <!-- 로딩 상태 -->
          <div v-if="isLoading" class="text-center py-5 text-muted">
            공지사항을 불러오는 중입니다...
          </div>

          <!-- 실제 폼 -->
          <template v-else>
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
          </template>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const router = useRouter()
const route = useRoute()

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const studyId = route.params.id as string | undefined
const noticeId = route.params.noticeId as string | undefined

// 상태
const title = ref('')
const markdown = ref('')
const submitting = ref(false)
const isLoading = ref(false)

// detail 페이지 경로 (취소 / 수정 후 이동)
const detailPath = computed(() => {
  if (!studyId || !noticeId) return '/studies'
  return `/studies/${studyId}/notice/${noticeId}`
})

/** 이미지 업로드 */
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
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'multipart/form-data',
        },
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

/** 기존 공지사항 불러오기 */
const fetchNoticeDetail = async () => {
  if (!studyId || !noticeId) {
    alert('잘못된 접근입니다. (ID 없음)')
    router.push('/studies')
    return
  }

  try {
    isLoading.value = true
    await ensureCsrf()

    const { data } = await axios.get(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
      {
        withCredentials: true,
      }
    )

    // 백엔드 응답 형태 예시:
    // {
    //   id, title, content, created_at, updated_at,
    //   author: {...}, study: {...}
    // }
    title.value = data.title ?? ''
    markdown.value = data.content ?? ''
  } catch (error) {
    console.error('공지 상세 조회 실패:', error)
    alert('공지사항 정보를 불러오지 못했습니다.')
  } finally {
    isLoading.value = false
  }
}

/** 공지사항 수정 */
const submitNotice = async () => {
  if (!studyId || !noticeId) {
    alert('잘못된 접근입니다. (ID 없음)')
    return
  }
  if (!title.value.trim()) {
    alert('제목을 입력하세요.')
    return
  }
  if (!markdown.value.trim()) {
    alert('내용을 입력하세요.')
    return
  }

  try {
    submitting.value = true
    await ensureCsrf()
    const csrfToken = getCookie('csrftoken')

    const payload = {
      title: title.value.trim(),
      content: markdown.value.trim(),
    }

    await axios.put(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
      payload,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      }
    )

    alert('공지사항이 수정되었습니다!')
    router.push(detailPath.value)
  } catch (error) {
    console.error(error)
    alert('공지사항 수정 중 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchNoticeDetail()
})
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
</style>
