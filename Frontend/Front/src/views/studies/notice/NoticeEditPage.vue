<!-- src/views/studies/NoticeEditPage.vue -->
<template>
  <AppShell>
    <!-- ✅ NoticeCreatePage와 동일한 레이아웃 패턴 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 notice-create-wrapper">
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
                  class="btn btn-light-outline btn-sm"
                >
                  취소
                </RouterLink>

                <button
                  class="btn btn-light-outline btn-sm btn-primary-outline"
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
                    previewTheme="github"
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
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import client from '@/api/client'
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

/** 이미지 업로드 - NoticeCreatePage와 동일한 엔드포인트 사용 */
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

    const { data } = await client.get(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
      {
        withCredentials: true,
      },
    )

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

    await client.put(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
      payload,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      },
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

/* ✅ NoticeCreatePage와 동일한 래퍼 */
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

/* 수정하기 버튼만 약한 파란 강조 */
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
