<!-- src/views/studies/NoticeDetailPage.vue -->
<template>
  <AppShell>
    <div class="notice-page">
      <div class="container-fluid py-4 d-flex justify-content-center">
        <!-- 중앙 포스트 카드 -->
        <div class="post-card shadow-sm">
          <!-- 상단 헤더 영역 -->
          <div class="post-header">
            <!-- 상단 작은 라벨 줄 -->
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="text-success fw-semibold small">
                공지사항
              </div>
              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                @click="goList"
              >
                이전
              </button>
            </div>

            <!-- 제목 -->
            <h1 class="post-title mb-2">
              {{ notice.title || '제목 없음' }}
            </h1>

            <!-- 작성자 / 작성일 -->
            <div class="d-flex align-items-center gap-2 text-muted small">
              <div class="avatar-circle">
                <span>{{ authorInitial }}</span>
              </div>
              <span class="fw-semibold text-dark">
                {{ displayAuthor || '작성자' }}
              </span>
              <span class="dot-separator">·</span>
              <span>{{ formatDate(notice.created_at) }}</span>
            </div>
          </div>

          <hr class="post-divider" />

          <!-- 본문 영역 -->
          <div class="post-body">
            <div class="notice-content" v-html="renderedContent"></div>

            <!-- 수정 시간 + 버튼 영역 -->
            <div class="post-footer d-flex flex-wrap justify-content-between align-items-center mt-4 pt-3 border-top">
              <div
                v-if="notice.updated_at"
                class="text-muted small mb-2 mb-md-0"
              >
                마지막 수정: {{ formatDate(notice.updated_at) }}
              </div>

              <div class="d-flex gap-2">
                <RouterLink
                  :to="`/studies/${studyId}/notice/${noticeId}/edit`"
                  class="btn btn-outline-primary btn-sm"
                >
                  수정
                </RouterLink>
                <button
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  @click="onDelete"
                >
                  삭제
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  @click="goList"
                >
                  목록
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- /post-card -->
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

const notice = ref({
  id: null,
  title: '',
  content: '',
  author: '',
  category: '',
  created_at: '',
  updated_at: '',
})

const md = new MarkdownIt({
  breaks: true,
  linkify: true,
})

const renderedContent = computed(() => {
  if (!notice.value.content) return ''
  return md.render(notice.value.content)
})

const displayAuthor = computed(() => {
  const raw = notice.value.author
  if (!raw) return ''
  if (typeof raw === 'string') return raw
  return raw.username || ''
})

const authorInitial = computed(() => {
  const name = displayAuthor.value || ''
  return name ? name[0].toUpperCase() : '?'
})

const formatDate = (dt) => {
  if (!dt) return ''
  return dt.replace('T', ' ').slice(0, 16)
}

const goList = () => {
  router.push(`/studies/${studyId}/notice`)
}

const onDelete = async () => {
  if (!confirm('이 공지를 삭제할까요? 삭제 후에는 되돌릴 수 없습니다.')) return

  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')

  try {
    await axios.delete(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
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
    const res = await axios.get(
      `${API_BASE}/studies/${studyId}/posts/notice_detail/${noticeId}/`,
      {
        params: { study_id: studyId, notice_id: noticeId },
        withCredentials: true,
        headers: { 'X-CSRFToken': csrftoken },
      }
    )
    console.log(res)
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
.notice-page {
  background-color: #f3f4f7;
  min-height: 100vh;
}

/* 중앙 카드: RLOA처럼 넓고 가운데 배치 */
.post-card {
  max-width: 960px;
  width: 100%;
  border-radius: 18px;
  background-color: #ffffff;
  overflow: hidden;
}

/* 헤더 영역 */
.post-header {
  padding: 1.5rem 1.75rem 0.75rem;
}

.post-title {
  font-size: 1.4rem;
  font-weight: 700;
}

/* 구분선 */
.post-divider {
  margin: 0 1.75rem;
  border-color: #e9ecef;
}

/* 작성자 라인 */
.avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #f1f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: #868e96;
}

.dot-separator {
  font-size: 0.8rem;
  line-height: 1;
}

/* 본문 */
.post-body {
  padding: 1.25rem 1.75rem 1.5rem;
}

/* Markdown 스타일 */
.notice-content {
  font-size: 0.98rem;
  line-height: 1.8;
  color: #212529;
}

.notice-content p {
  margin-bottom: 0.8rem;
}

.notice-content h1,
.notice-content h2,
.notice-content h3,
.notice-content h4 {
  margin-top: 1.4rem;
  margin-bottom: 0.7rem;
  font-weight: 600;
}

.notice-content ul,
.notice-content ol {
  padding-left: 1.25rem;
  margin-bottom: 0.7rem;
}

.notice-content code {
  padding: 0.15rem 0.3rem;
  border-radius: 4px;
  background-color: #f1f3f5;
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 0.9em;
}

.notice-content pre code {
  display: block;
  padding: 0.9rem;
  border-radius: 6px;
  background-color: #f8f9fa;
  overflow-x: auto;
}

/* 반응형 */
@media (max-width: 576px) {
  .post-card {
    border-radius: 0;
  }

  .post-header {
    padding: 1.25rem 1.1rem 0.75rem;
  }

  .post-divider {
    margin: 0 1.1rem;
  }

  .post-body {
    padding: 1rem 1.1rem 1.25rem;
  }

  .post-title {
    font-size: 1.2rem;
  }
}
</style>
