<template>
  <div v-if="show" class="study-manage-backdrop">
    <div class="study-manage-modal">
      <div class="card shadow-sm">
        <div
          class="card-header d-flex justify-content-between align-items-center"
        >
          <div>
            <h5 class="mb-0 fw-bold">스터디 관리</h5>
            <small class="text-muted">
              {{ studyTitle }} (코드:
              <span class="fw-semibold">{{ studyId }}</span>)
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
          <!-- 일반 회원 뷰 -->
          <div v-if="!isLeader">
            <p class="mb-3">
              이 스터디의 참여 코드는
              <span class="badge bg-primary-subtle text-primary ms-1">
                {{ studyId }}
              </span>
              입니다.
            </p>
            <p class="text-muted small mb-4">
              스터디를 탈퇴하면 더 이상 일정, 공지, 시험에 접근할 수 없어요.
            </p>

            <div class="d-flex justify-content-end">
              <button
                type="button"
                class="btn btn-outline-secondary me-2"
                @click="$emit('close')"
              >
                닫기
              </button>
              <button
                type="button"
                class="btn btn-outline-danger"
                @click="$emit('leave')"
              >
                스터디 탈퇴
              </button>
            </div>
          </div>

          <!-- 리더 뷰 -->
          <div v-else>
            <!-- 스터디 코드 섹션 -->
            <div class="mb-4">
              <h6 class="fw-semibold mb-2">스터디 정보</h6>
              <div class="d-flex flex-wrap align-items-center gap-2">
                <span class="badge bg-primary-subtle text-primary">
                  코드: {{ studyId }}
                </span>
                <span class="text-muted small">
                  이 코드를 스터디원들에게 공유해 참여를 받을 수 있어요.
                </span>
              </div>
            </div>

            <!-- 스터디 삭제 섹션 -->
            <div class="mb-4">
              <h6 class="fw-semibold mb-2 text-danger">스터디 삭제</h6>
              <p class="text-muted small mb-2">
                스터디를 삭제하면 일정, 공지사항, 시험 등 모든 데이터가
                삭제되며 복구할 수 없습니다.
              </p>
              <button
                type="button"
                class="btn btn-outline-danger btn-sm"
                @click="$emit('delete-study')"
              >
                스터디 삭제
              </button>
            </div>

            <!-- 멤버 관리 섹션 -->
            <div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="fw-semibold mb-0">스터디 멤버 관리</h6>
                <span class="badge bg-light text-muted small">
                  {{ members.length }}명
                </span>
              </div>

              <p class="text-muted small mb-2">
                아래 목록에서 스터디원을 확인하고 필요할 경우 강제 탈퇴시킬 수
                있습니다.
              </p>

              <div v-if="membersError" class="alert alert-danger py-2 small">
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
                  class="list-group list-group-flush rounded border small"
                >
                  <li
                    v-for="m in members"
                    :key="m.id"
                    class="list-group-item d-flex align-items-center justify-content-between"
                  >
                    <div class="d-flex align-items-center">
                      <img
                        v-if="m.profile_img"
                        :src="m.profile_img"
                        alt="avatar"
                        class="member-avatar me-2"
                        referrerpolicy="no-referrer"
                      />
                      <div v-else class="member-avatar member-avatar-fallback me-2">
                        {{ initials(m.username) }}
                      </div>

                      <div>
                        <div class="fw-semibold">
                          {{ m.username }}
                        </div>
                        <div class="text-muted">
                          <span class="badge bg-light text-muted me-1">
                            {{ roleLabel(m.role) }}
                          </span>
                          <span class="small">{{ m.email }}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <!-- 리더는 강퇴 버튼 비활성화 -->
                      <button
                        v-if="m.role !== 'leader'"
                        type="button"
                        class="btn btn-outline-danger btn-sm"
                        @click="$emit('kick', m.id)"
                      >
                        강제 탈퇴
                      </button>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            <div class="d-flex justify-content-end mt-4">
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="$emit('close')"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
        <!-- /card-body -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface StudyMember {
  id: number
  username: string
  email: string
  profile_img: string | null
  role: string
}

const props = defineProps<{
  show: boolean
  isLeader: boolean
  studyId: number
  studyTitle: string
  members: StudyMember[]
  loadingMembers: boolean
  membersError: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'leave'): void
  (e: 'delete-study'): void
  (e: 'kick', memberId: number): void
}>()

function initials(name: string) {
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] ?? ''
  const last = parts[1]?.[0] ?? ''
  return (first + last).toUpperCase()
}

function roleLabel(role: string) {
  if (role === 'leader') return '리더'
  if (role === 'sub_leader') return '부리더'
  return '멤버'
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
</style>
