<!-- src/views/studies/notice/NoticeDetailPage.vue -->
<template>
  <AppShell>
    <div class="notice-page">
      <div class="container-fluid py-4 d-flex justify-content-center">
        <!-- 중앙 포스트 카드 -->
        <div class="post-card shadow-sm">
          <!-- 상단 헤더 영역 -->
          <div class="post-header">
            <!-- 상단 라벨 줄 -->
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div class="text-success fw-semibold small">
                공지사항
              </div>
              <button type="button" class="btn btn-light-outline btn-sm" @click="goList">
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
                <!-- 프로필 이미지 있을 때 -->
                <template v-if="notice.author && notice.author.profile_img">
                  <img :src="profileImg" alt="프로필 이미지" class="avatar-img" />
                </template>

                <!-- 없을 때: Bootstrap 사람 아이콘 -->
                <template v-else>
                  <i class="bi bi-person-fill text-secondary" aria-hidden="true"></i>
                </template>
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
            <!-- ✅ md-editor-v3 Preview로 렌더링: 작성 화면과 거의 동일 UI -->
            <MdPreview class="notice-content" :id="previewId" :modelValue="notice.content || ''" theme="light"
              previewTheme="github" :showCodeRowNumber="true" language="en-US" />

            <!-- 수정 시간 + 버튼 영역 -->
            <div class="post-footer d-flex flex-wrap justify-content-between align-items-center mt-4 pt-3 border-top">
              <div v-if="notice.updated_at" class="text-muted small mb-2 mb-md-0">
                마지막 수정: {{ formatDate(notice.updated_at) }}
              </div>

              <div class="d-flex gap-2">
                <RouterLink :to="`/studies/${studyId}/notice/${noticeId}/edit`"
                  class="btn btn-light-outline btn-sm btn-primary-outline">
                  수정
                </RouterLink>
                <button type="button" class="btn btn-light-outline btn-sm btn-danger-outline" @click="onDelete">
                  삭제
                </button>
                <button type="button" class="btn btn-light-outline btn-sm" @click="goList">
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
import { MdPreview } from 'md-editor-v3'
import AppShell from '@/layouts/AppShell.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors.ts'

const route = useRoute()
const router = useRouter()

const studyId = route.params.id
const noticeId = route.params.noticeId
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const previewId = 'notice-preview' // MdPreview용 id (고정이면 충분)

// 공지 데이터
const notice = ref({
  id: null,
  title: '',
  content: '',
  author: '',
  category: '',
  created_at: '',
  updated_at: '',
})

const displayAuthor = computed(() => {
  const raw = notice.value.author
  if (!raw) return ''
  if (typeof raw === 'string') return raw
  return raw.username || ''
})

const profileImg = computed(() => {
  if (!notice.value?.author?.profile_img) return '/default-avatar.png'

  const path = notice.value.author.profile_img

  if (path.startsWith('http')) return path

  return `${API_BASE.replace(/\/$/, '')}${path}`
})

const formatDate = dt => {
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
  min-height: 100vh;
  width: 100%;
  max-width: 1300px;
  /* 전체 폭 중앙 정렬 */
  padding-left: 1rem;
  /* 항상 좌우 여백 유지 */
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 768px) {
  .notice-page {
    max-width: 1300px;
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

/* 중앙 카드 */
.post-card {
  max-width: 1300px;
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

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.dot-separator {
  font-size: 0.8rem;
  line-height: 1;
}

/* 본문 */
.post-body {
  padding: 1.25rem 1.75rem 1.5rem;
}

/* md-editor-v3 프리뷰 전체 래퍼 */
.notice-content {
  /* 필요하면 위아래 간격만 살짝 조절 */
  margin-top: 0.25rem;
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

/* 라이트 아웃라인 공통 버튼 */
.btn-light-outline {
  border: 1px solid #d0d7e2;
  background-color: #ffffff;
  color: #475569;
  border-radius: 8px;
  transition: 0.2s ease;
  padding: 0.375rem 0.75rem; /* btn-sm 크기 */
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

/* disabled 공통 */
.btn-light-outline:disabled,
.btn-light-outline.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 수정 버튼용: 파란 포인트 */
.btn-primary-outline {
  color: #2563eb;
  border-color: #93c5fd;
}

.btn-primary-outline:hover {
  background-color: #eff6ff;
  border-color: #60a5fa;
  color: #1d4ed8;
}

/* 삭제 버튼용: 레드 포인트 */
.btn-danger-outline {
  color: #dc2626;
  border-color: #fecaca;
}

.btn-danger-outline:hover {
  background-color: #fef2f2;
  border-color: #fca5a5;
  color: #b91c1c;
}

</style>
