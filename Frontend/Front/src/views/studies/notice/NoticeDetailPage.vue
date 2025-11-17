<!-- src/views/studies/NoticeDetailPage.vue -->
<template>
  <AppShell>
    <div class="container-fluid py-4 d-flex flex-column align-items-center">
      <!-- 상단 헤더 -->
      <div
        class="d-flex align-items-center justify-content-between mb-4 w-100"
        style="max-width: 950px"
      >
        <h2 class="fw-bold mb-0 ms-1">공지사항</h2>
        <RouterLink :to="`/studies/${studyId}/notice`" class="btn btn-outline-secondary">
          목록으로
        </RouterLink>
      </div>

      <!-- 본문 카드 -->
      <div class="card shadow-sm w-100" style="max-width: 950px">
        <div class="card-body">
          <!-- 제목 + 수정/삭제 버튼 -->
          <div class="d-flex justify-content-between align-items-start mb-3">
            <h3 class="fw-bold mb-0 ms-1">{{ notice.title }}</h3>

            <div class="btn-group btn-group-sm">
              <RouterLink
                :to="`/studies/${studyId}/notice/${noticeId}/edit`"
                class="btn btn-outline-primary"
              >
                수정
              </RouterLink>

              <button
                type="button"
                class="btn btn-outline-danger"
                @click="onDelete"
              >
                삭제
              </button>
            </div>
          </div>

          <!-- 작성자 정보 -->
          <div class="d-flex align-items-center mb-4 text-muted small">
            <span class="fw-semibold text-dark me-2">{{ notice.author }}</span>
            <span>· {{ formatDate(notice.created_at) }}</span>
          </div>

          <!-- 내용 -->
          <div class="notice-content" v-html="renderedContent"></div>

          <!-- 수정 일시 -->
          <div class="text-muted mt-4 small">
            <span v-if="notice.updated_at">
              마지막 수정: {{ formatDate(notice.updated_at) }}
            </span>
          </div>

        </div>
      </div>
    </div>
  </AppShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import MarkdownIt from 'markdown-it'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const route = useRoute()
const router = useRouter()

const studyId = route.params.id
const noticeId = route.params.noticeId
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// 공지 데이터 기본값
const notice = ref({
  id: null,
  title: '',
  content: '',
  author: '',
  created_at: '',
  updated_at: '',
})

// Markdown 렌더러
const md = new MarkdownIt({
  breaks: true,
  linkify: true,
})

const renderedContent = computed(() => {
  if (!notice.value.content) return ''
  return md.render(notice.value.content)
})

// 날짜 포맷
const formatDate = (dt) => {
  if (!dt) return ''
  return dt.replace('T', ' ').slice(0, 16)
}

// 삭제
const onDelete = async () => {
  if (!confirm('이 공지를 삭제할까요? 삭제 후에는 되돌릴 수 없습니다.')) return

  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')

  try {
    await axios.post(
      `${API_BASE}/posts/delete_notice/`,
      {
        study_id: studyId,
        notice_id: noticeId,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
        },
      }
    )

    router.push(`/studies/${studyId}/notice`)
  } catch (err) {
    console.error(err)
    const status = err.response?.status

    if (status === 401 || status === 403) {
      alert('삭제 권한이 없습니다.')
    } else {
      alert('공지 삭제 중 오류가 발생했습니다.')
    }
  }
}

onMounted(async () => {
  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')

  try {
    const res = await axios.get(`${API_BASE}/posts/read_notice/`, {
      params: { study_id: studyId, notice_id: noticeId },
      withCredentials: true,
      headers: { 'X-CSRFToken': csrftoken },
    })

    notice.value = { ...notice.value, ...res.data }
  } catch (err) {
    console.error(err)
    const status = err.response?.status

    if (status === 404) {
      alert('존재하지 않는 공지입니다.')
      router.push(`/studies/${studyId}/notice`)
    } else if (status === 401) {
      alert('로그인이 필요합니다.')
      router.push('/login')
    } else {
      alert('공지 정보를 불러오는 중 오류가 발생했습니다.')
    }
  }
})
</script>

<style scoped>
.notice-content {
  font-size: 1rem;
  line-height: 1.7;
}

/* Markdown 스타일 */
.notice-content h1,
.notice-content h2,
.notice-content h3,
.notice-content h4 {
  font-weight: 600;
  margin-top: 1.2rem;
  margin-bottom: 0.6rem;
}

.notice-content p {
  margin-bottom: 0.6rem;
}

.notice-content ul,
.notice-content ol {
  padding-left: 1.25rem;
  margin-bottom: 0.6rem;
}

.notice-content code {
  padding: 0.15rem 0.3rem;
  border-radius: 4px;
  background-color: #f5f5f5;
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 0.9em;
}

.notice-content pre code {
  display: block;
  padding: 0.75rem;
  overflow-x: auto;
}
</style>
