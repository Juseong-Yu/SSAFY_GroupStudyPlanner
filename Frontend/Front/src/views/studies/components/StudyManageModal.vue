<!-- src/components/StudyManageModal.vue -->
<template>
  <div v-if="show" class="study-manage-backdrop">
    <div class="study-manage-modal">
      <div class="card shadow-sm">
        <!-- 헤더 영역 (시원하게 개선됨) -->
        <div class="modal-header-custom d-flex justify-content-between align-items-start">
          <div class="d-flex flex-column">
            <h5 class="fw-bold mb-1">스터디 관리</h5>

            <div class="study-title-text">
              {{ studyTitle }}
            </div>
          </div>

          <button type="button" class="btn-close" aria-label="Close" @click="$emit('close')"></button>
        </div>

        <div class="card-body">
          <!-- 1. 내 정보 (리뉴얼 섹션) -->
          <div class="mb-4">
            <div class="info-section small">
              <!-- 내 역할 -->
              <div class="info-row mb-2">
                <div class="d-flex align-items-center gap-2">
                  <div class="info-icon role">
                    <i class="bi bi-person-badge"></i>
                  </div>
                  <div>
                    <div class="info-label">내 역할</div>
                    <div class="info-value">
                      {{ roleLabel(myRole) }}
                    </div>
                  </div>
                </div>

                <span class="info-chip">
                  {{ roleLabel(myRole) }}
                </span>
              </div>

              <!-- 참여 코드 -->
              <div class="info-row">
                <div class="d-flex align-items-center gap-2">
                  <div class="info-icon code">
                    <i class="bi bi-key"></i>
                  </div>
                  <div>
                    <div class="info-label">스터디 참여 코드</div>
                    <div class="d-flex align-items-center gap-2 mt-1">
                      <span class="study-code-box">
                        {{ displayedStudyCode }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="d-flex align-items-center gap-1">
                  <button type="button" class="btn-icon-ghost" @click="toggleStudyCode"
                    :aria-label="showStudyCode ? '참여 코드 숨기기' : '참여 코드 보기'">
                    <i :class="showStudyCode ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. (리더 전용) 멤버 관리 -->
          <div v-if="isLeader" class="mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="fw-semibold mb-0">스터디 멤버 관리</h6>
              <span class="badge bg-light text-muted small">
                {{ members.length }}명
              </span>
            </div>

            <div v-if="membersError" class="alert alert-danger py-2 small mb-2">
              {{ membersError }}
            </div>

            <div v-if="loadingMembers" class="text-center text-muted small py-3">
              멤버 목록을 불러오는 중입니다...
            </div>

            <div v-else>
              <div v-if="!members.length" class="text-center text-muted small py-3">
                아직 등록된 멤버가 없어요.
              </div>

              <ul v-else class="list-group list-group-flush rounded border small member-list-group">
                <li v-for="m in members" :key="m.id"
                  class="list-group-item member-list-item d-flex align-items-center justify-content-between">
                  <div class="d-flex align-items-center gap-2">
                    <img v-if="m.profile_img" :src="m.profile_img" alt="avatar" class="member-avatar"
                      referrerpolicy="no-referrer" />
                    <div v-else class="member-avatar member-avatar-fallback">
                      {{ initials(m.username) }}
                    </div>

                    <div>
                      <div class="fw-semibold">
                        {{ m.username }}
                      </div>
                      <div class="text-muted small">
                        {{ m.email }}
                      </div>
                    </div>
                  </div>

                  <div class="d-flex align-items-center gap-2">
                    <!-- 리더 자신은 역할/추방 불가 -->
                    <template v-if="m.role === 'leader'">
                      <span class="badge bg-primary-subtle text-primary">
                        리더
                      </span>
                    </template>

                    <template v-else>
                      <!-- 역할 선택 -->
                      <select class="form-select form-select-sm w-auto" :value="m.role"
                        @change="onRoleChange(m.id, $event)">
                        <option value="admin">관리자</option>
                        <option value="member">멤버</option>
                      </select>

                      <!-- 추방 -->
                      <button type="button" class="btn btn-outline-danger btn-sm" @click="$emit('kick', m.id)">
                        추방
                      </button>
                    </template>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- 3. 스터디 나가기 (공통, 리더는 비활성) -->
          <div class="mb-3 border rounded p-3 bg-light-subtle">
            <h6 class="fw-semibold mb-2">스터디 나가기</h6>
            <p class="text-muted small mb-3">
              스터디를 나가면 더 이상 일정, 공지, 시험에 접근할 수 없습니다.
            </p>

            <div class="d-flex justify-content-end align-items-center gap-2">
              <span v-if="myRole === 'leader'" class="text-danger small me-auto">
                리더는 스터디를 해산해야만 나갈 수 있습니다.
              </span>

              <button type="button" class="btn btn-danger btn-sm" :disabled="myRole === 'leader'"
                @click="$emit('leave')">
                스터디 나가기
              </button>
            </div>
          </div>

          <!-- 4. (리더 전용) 스터디 해산 -->
          <div v-if="isLeader" class="border rounded p-3 danger-section mb-2">
            <h6 class="fw-semibold mb-2 text-danger d-flex align-items-center gap-1">
              <i class="bi bi-exclamation-triangle-fill"></i>
              스터디 해산
            </h6>
            <p class="text-muted small mb-3">
              스터디를 해산하면 일정, 공지사항, 시험 등 모든 데이터가 삭제되며
              복구할 수 없습니다.
            </p>
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-outline-danger btn-sm" @click="$emit('dissolve')">
                스터디 해산
              </button>
            </div>
          </div>

          <!-- 5. 맨 아래 공통 닫기 버튼 -->
          <div class="d-flex justify-content-end mt-3">
            <button type="button" class="btn btn-light-outline btn-sm" @click="$emit('close')">
              닫기
            </button>
          </div>
        </div>
        <!-- /card-body -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { StudyRole } from '@/stores/studyRoleStore'

interface StudyMember {
  id: number
  username: string
  email: string
  profile_img: string | null
  role: StudyRole
}

const props = defineProps<{
  show: boolean
  isLeader: boolean
  myRole: StudyRole
  studyId: number
  studyTitle: string
  members: StudyMember[]
  loadingMembers: boolean
  membersError: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'leave'): void
  (e: 'dissolve'): void
  (e: 'kick', memberId: number): void
  (e: 'change-role', memberId: number, role: StudyRole): void
}>()

const showStudyCode = ref(false)

const displayedStudyCode = computed(() => {
  const raw = String(props.studyId ?? '')
  if (!raw) return ''
  if (showStudyCode.value) return raw
  return '•'.repeat(raw.length)
})

function toggleStudyCode() {
  showStudyCode.value = !showStudyCode.value
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] ?? ''
  const last = parts[1]?.[0] ?? ''
  return (first + last).toUpperCase()
}

function roleLabel(role: StudyRole) {
  if (role === 'leader') return '리더'
  if (role === 'admin') return '관리자'
  return '멤버'
}

function onRoleChange(memberId: number, e: Event) {
  const target = e.target as HTMLSelectElement
  const value = target.value as StudyRole
  emit('change-role', memberId, value)
}
</script>

<style scoped>
/* 시원해진 모달 헤더 영역 */
.modal-header-custom {
  padding: 1rem 1.5rem;        /* 여백 크게 */
  background: white;             /* 카드와 통일 */
  border-bottom: 1px solid #e5e9f0;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

/* 스터디 타이틀 텍스트 */
.study-title-text {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 0.2rem;
}

.study-manage-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

/* ✅ 모달 사이즈 확장된 버전 */
.study-manage-modal {
  width: 100%;
  max-width: 760px;
  /* 기존 640px → 760px */
  margin: 0 1.25rem;
}

.study-manage-modal .card {
  max-height: 90vh;
  /* 기존 80vh → 85vh */
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  border: 1px solid #dee3ea;
}

.study-manage-modal .card-body {
  padding: 1.5rem !important;
  overflow-y: auto;
}

/* 모바일에서는 너무 크지 않게 */
@media (max-width: 768px) {
  .study-manage-modal {
    max-width: 100%;
    margin: 0 1rem;
  }

  .study-manage-modal .card {
    max-height: 90vh;
  }
}

/* ✅ 상단 내 정보 섹션 */
.info-section {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 0.75rem 1rem;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.info-row+.info-row {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #e2e8f0;
}

.info-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  font-weight: 600;
}

.info-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.info-chip {
  padding: 0.3rem 0.85rem;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.info-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.info-icon.role {
  background: #eef2ff;
  color: #4f46e5;
}

.info-icon.code {
  background: #ecfdf3;
  color: #16a34a;
}

/* 멤버 아바타 */
.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  object-fit: cover;
}

.member-avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #e9eef7;
  color: #2b3a67;
  font-size: 0.8rem;
  font-weight: 700;
}

/* 멤버 리스트 비주얼 디테일 */
.member-list-group {
  border-radius: 12px;
}

.member-list-item {
  padding-top: 0.55rem;
  padding-bottom: 0.55rem;
}

/* 해산 섹션 위험 강조 */
.danger-section {
  background-color: #fff5f5;
}

/* 참여 코드 박스 */
.study-code-box {
  min-width: 96px;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1px dashed #cbd5e1;
  background-color: #ffffff;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    'Liberation Mono', 'Courier New', monospace;
  letter-spacing: 0.08em;
  text-align: center;
  font-size: 0.8rem;
  color: #0f172a;
}

/* 눈 아이콘 버튼 (고스트 스타일) */
.btn-icon-ghost {
  border: none;
  background: transparent;
  padding: 0.25rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.btn-icon-ghost:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}
</style>
