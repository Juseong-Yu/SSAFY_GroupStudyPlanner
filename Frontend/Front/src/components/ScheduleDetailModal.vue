<!-- src/components/ScheduleDetailModal.vue -->
<template>
  <div v-if="show" class="schedule-modal-backdrop">
    <div class="schedule-modal">
      <div class="card shadow-sm">
        <div class="card-header d-flex justify-content-between align-items-start flex-wrap gap-2">
          <!-- 제목 -->
          <h5 class="mb-1 fw-bold">
            {{ detail?.data.schedule.title || '일정 상세' }}
          </h5>

          <!-- 오른쪽: 타입 배지 + (개인일정일 때) 수정/삭제 + 닫기 버튼 -->
          <div class="d-flex align-items-center gap-2 ms-auto">
            <span v-if="detail" class="badge rounded-pill small" :class="detail.type === 'study'
                ? 'bg-primary-subtle text-primary'
                : 'bg-purple-subtle text-purple'
              ">
              {{ detail.type === 'study' ? '스터디 일정' : '개인 일정' }}
            </span>

            <!-- ✅ 개인 일정일 때만 수정/삭제 버튼 노출 -->
            <template v-if="detail && detail.type === 'personal'">
              <button type="button" class="btn btn-ghost btn-sm" @click="onClickEdit">
                수정
              </button>
              <button type="button" class="btn btn-ghost-danger btn-sm" @click="onClickDelete">
                삭제
              </button>
            </template>

            <button type="button" class="btn btn-light btn-sm" @click="emit('close')">
              닫기
            </button>

          </div>
        </div>

        <div class="card-body">
          <div v-if="error" class="alert alert-danger py-2 small mb-3">
            {{ error }}
          </div>

          <div v-if="!detail && !error" class="py-4 text-center text-muted small">
            일정을 불러오는 중입니다...
          </div>

          <template v-else-if="detail">
            <div class="row g-4 align-items-start">
              <!-- 왼쪽: 정보 -->
              <div class="col-12 col-md-7">
                <!-- ✅ 스터디 일정이면 스터디명 표시 -->
                <div v-if="detail.type === 'study' && detail.data.study" class="mb-2 small text-muted">
                  {{ detail.data.study.name }}
                </div>

                <!-- 스터디 일정일 때만 작성자 정보 -->
                <template v-if="detail.type === 'study' && detail.data.author">
                  <div class="d-flex align-items-center mb-3">
                    <div v-if="detailAuthorAvatar" class="rounded-circle border bg-light me-3 overflow-hidden"
                      style="width: 44px; height: 44px">
                      <img :src="detailAuthorAvatar" alt="author" class="w-100 h-100" style="object-fit: cover" />
                    </div>
                    <div v-else
                      class="rounded-circle border bg-light me-3 d-flex align-items-center justify-content-center"
                      style="width: 44px; height: 44px; font-size: 0.8rem">
                      <i class="bi bi-person-fill text-secondary" aria-hidden="true"></i>
                    </div>

                    <div class="small">
                      <div class="fw-semibold">
                        {{ detail.data.author!.username }}
                      </div>
                      <div class="text-muted">
                        {{ detail.data.author!.email }}
                      </div>
                    </div>
                  </div>

                  <hr class="my-3" />
                </template>

                <!-- 제목 / 설명 -->
                <div class="mb-4">
                  <div class="fw-semibold small text-muted mb-1">일정 제목</div>
                  <div class="fs-6">{{ detail.data.schedule.title }}</div>
                </div>

                <div class="mb-0">
                  <div class="fw-semibold small text-muted mb-1">일정 상세</div>
                  <p class="mb-0 small text-body" style="white-space: pre-wrap">
                    {{ detail.data.schedule.description || '내용 없음' }}
                  </p>
                </div>
              </div>

              <!-- 오른쪽: 시간 요약 -->
              <div class="col-12 col-md-5">
                <div class="time-summary p-3 rounded-3 border small">
                  <div class="fw-semibold mb-3 d-flex align-items-center gap-2">
                    <span>시간 요약</span>
                  </div>

                  <div class="mb-3">
                    <div class="text-muted fw-semibold mb-1">시작</div>
                    <div>{{ formatShortDateUtc(detail.data.schedule.start_at) }}</div>
                    <div>{{ formatTimeUtc(detail.data.schedule.start_at) }}</div>
                  </div>

                  <div>
                    <div class="text-muted fw-semibold mb-1">종료</div>
                    <div>
                      {{
                        formatShortDateUtc(
                          detail.data.schedule.end_at || detail.data.schedule.start_at,
                        )
                      }}
                    </div>
                    <div>
                      {{
                        formatTimeUtc(
                          detail.data.schedule.end_at || detail.data.schedule.start_at,
                        )
                      }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

/** ===== 타입 정의 (MainPage StoredEvent와 동일 구조) ===== **/
export type ScheduleType = 'study' | 'personal'

export interface CombinedScheduleCore {
  title: string
  description: string
  start_at: string
  end_at?: string | null
}

export interface CombinedAuthor {
  id: number
  username: string
  email: string
  profile_img: string | null
}

export interface CombinedStudy {
  id: number
  name: string
}

export interface CombinedData {
  id: number
  schedule: CombinedScheduleCore
  author?: CombinedAuthor
  study?: CombinedStudy
  [key: string]: any
}

export interface StoredEvent {
  type: ScheduleType
  data: CombinedData
}

const props = defineProps<{
  show: boolean
  error: string
  detail: StoredEvent | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'delete', id: number): void
  (e: 'edit', payload: StoredEvent): void
}>()

/* 날짜 유틸 (UTC 기준) */
const parseUtc = (value: string): Date => {
  if (!value) return new Date(NaN)
  return new Date(value)
}

const formatTimeUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ''
  const h = String(d.getUTCHours()).padStart(2, '0')
  const m = String(d.getUTCMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

const formatShortDateUtc = (value: string): string => {
  const d = parseUtc(value)
  if (isNaN(d.getTime())) return ''
  const month = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  return `${month}월 ${day}일`
}

/* 작성자 아바타 */
const detailAuthorAvatar = computed(() => {
  const d = props.detail
  const author = d?.data.author
  if (!author || !author.profile_img) return null
  return `${API_BASE}${author.profile_img}`
})

/* ✅ 개인 일정 수정 */
const onClickEdit = () => {
  if (!props.detail) return
  emit('edit', props.detail)
}

/* ✅ 개인 일정 삭제 */
const onClickDelete = () => {
  if (!props.detail) return
  if (!window.confirm('이 개인 일정을 삭제할까요?')) return
  emit('delete', props.detail.data.id)
}
</script>

<style scoped>
.schedule-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.schedule-modal {
  width: 100%;
  max-width: 760px;
  padding: 0 1rem;
}

.schedule-modal .card {
  border-radius: 18px;
  border: none;
}

.schedule-modal .card-header {
  padding: 1.25rem 1.75rem 1rem;
}

.schedule-modal .card-body {
  padding: 1.5rem 1.75rem 1.75rem;
}

.schedule-modal .card-header .btn {
  white-space: nowrap;
  padding-inline: 0.9rem;
}

.schedule-modal h5 {
  font-size: 1.1rem;
}

/* 시간 요약 박스 */
.time-summary {
  background: #f7f9fc;
}

/* 개인 일정 배지 색상 */
.bg-purple-subtle {
  background-color: #f3e8ff;
}

.text-purple {
  color: #6b21a8;
}

/* 헤더 안 고스트 버튼 (수정/삭제) */
.btn-ghost {
  border: none;
  background: transparent;
  color: #6b7280; /* slate-500 */
  padding: 0.15rem 0.45rem;
  font-size: 0.8rem;
  border-radius: 999px;
}

.btn-ghost:hover {
  background-color: rgba(148, 163, 184, 0.12); /* slate-400 alpha */
  color: #374151; /* slate-700 */
}

.btn-ghost-danger {
  border: none;
  background: transparent;
  color: #b91c1c; /* red-700 */
  padding: 0.15rem 0.45rem;
  font-size: 0.8rem;
  border-radius: 999px;
}

.btn-ghost-danger:hover {
  background-color: rgba(248, 113, 113, 0.08); /* red-400 alpha */
  color: #991b1b; /* red-800 */
}

</style>
