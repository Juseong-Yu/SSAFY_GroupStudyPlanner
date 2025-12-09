<!-- src/components/StudyManageModal.vue -->
<template>
  <div v-if="show" class="study-manage-backdrop">
    <div class="study-manage-modal">
      <div class="card shadow-sm">
        <!-- 헤더 -->
        <div
          class="card-header d-flex justify-content-between align-items-center"
        >
          <div>
            <h5 class="mb-0 fw-bold">스터디 관리</h5>
            <small class="text-muted">
              {{ studyTitle }}
            </small>
          </div>

          <button
            type="button"
            class="btn-close"
            aria-label="Close"
            @click="$emit('close')"
          ></button>
        </div>

        <div class="card-body">
          <!-- 1. 내 정보 -->
          <div class="mb-4">
            <h6 class="fw-semibold mb-2">나의 정보</h6>
            <div class="d-flex flex-wrap align-items-center gap-2 small">
              <span class="badge bg-light text-muted">
                내 역할: {{ roleLabel(myRole) }}
              </span>
              <span class="badge bg-primary-subtle text-primary">
                참여 코드: {{ studyId }}
              </span>
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

            <p class="text-muted small mb-2">
              각 멤버의 역할을 변경하거나, 필요시 스터디에서 내보낼 수 있습니다.
            </p>

            <div v-if="membersError" class="alert alert-danger py-2 small mb-2">
              {{ membersError }}
            </div>

            <div
              v-if="loadingMembers"
              class="text-center text-muted small py-3"
            >
              멤버 목록을 불러오는 중입니다...
            </div>

            <div v-else>
              <div
                v-if="!members.length"
                class="text-center text-muted small py-3"
              >
                아직 등록된 멤버가 없어요.
              </div>

              <ul
                v-else
                class="list-group list-group-flush rounded border small member-list-group"
              >
                <li
                  v-for="m in members"
                  :key="m.id"
                  class="list-group-item member-list-item d-flex align-items-center justify-content-between"
                >
                  <div class="d-flex align-items-center gap-2">
                    <img
                      v-if="m.profile_img"
                      :src="m.profile_img"
                      alt="avatar"
                      class="member-avatar"
                      referrerpolicy="no-referrer"
                    />
                    <div
                      v-else
                      class="member-avatar member-avatar-fallback"
                    >
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
                      <select
                        class="form-select form-select-sm w-auto"
                        :value="m.role"
                        @change="onRoleChange(m.id, $event)"
                      >
                        <option value="admin">관리자</option>
                        <option value="member">멤버</option>
                      </select>

                      <!-- 추방 -->
                      <button
                        type="button"
                        class="btn btn-outline-danger btn-sm"
                        @click="$emit('kick', m.id)"
                      >
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
              <span
                v-if="myRole === 'leader'"
                class="text-danger small me-auto"
              >
                리더는 스터디를 해산해야만 나갈 수 있습니다.
              </span>

              <button
                type="button"
                class="btn btn-danger btn-sm"
                :disabled="myRole === 'leader'"
                @click="$emit('leave')"
              >
                스터디 나가기
              </button>
            </div>
          </div>

          <!-- 4. (리더 전용) 스터디 해산 -->
          <div v-if="isLeader" class="border rounded p-3 danger-section mb-2">
            <h6
              class="fw-semibold mb-2 text-danger d-flex align-items-center gap-1"
            >
              <!-- 부트스트랩 아이콘 사용 (설정되어 있다면) -->
              <i class="bi bi-exclamation-triangle-fill"></i>
              스터디 해산
            </h6>
            <p class="text-muted small mb-3">
              스터디를 해산하면 일정, 공지사항, 시험 등 모든 데이터가 삭제되며
              복구할 수 없습니다.
            </p>
            <div class="d-flex justify-content-end">
              <button
                type="button"
                class="btn btn-outline-danger btn-sm"
                @click="$emit('dissolve')"
              >
                스터디 해산
              </button>
            </div>
          </div>

          <!-- 5. 맨 아래 공통 닫기 버튼 -->
          <div class="d-flex justify-content-end mt-3">
            <button
              type="button"
              class="btn btn-light-outline btn-sm"
              @click="$emit('close')"
            >
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
.study-manage-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.study-manage-modal {
  width: 100%;
  max-width: 640px;
  margin: 0 1rem;
}

/* 카드 자체를 모달처럼 조정 */
.study-manage-modal .card {
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.study-manage-modal .card-body {
  overflow-y: auto;
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
</style>
