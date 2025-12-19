<!-- src/components/StudyManageModal.vue -->
<template>
  <div v-if="show" class="study-manage-backdrop">
    <div class="study-manage-modal">
      <div class="card shadow-sm">
        <!-- 헤더 -->
        <div class="modal-header-custom d-flex justify-content-between align-items-start">
          <div class="d-flex flex-column">
            <h5 class="fw-bold mb-1">스터디 관리</h5>
            <div class="study-title-text">
              {{ studyTitle }}
            </div>
          </div>

          <button
            type="button"
            class="btn-close"
            aria-label="Close"
            @click="$emit('close')"
          ></button>
        </div>

        <div class="card-body">
          <!-- 1) 내 정보 -->
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
                  <button
                    type="button"
                    class="btn-icon-ghost"
                    @click="toggleStudyCode"
                    :aria-label="showStudyCode ? '참여 코드 숨기기' : '참여 코드 보기'"
                  >
                    <i :class="showStudyCode ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ✅ Discord 설정 -->
          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="fw-semibold mb-0">Discord 설정</h6>
              <span class="badge bg-light text-muted small">
                {{ discordGuild ? '연결됨' : '미연결' }}
              </span>
            </div>

            <div v-if="discordError" class="alert alert-danger py-2 small mb-2">
              {{ discordError }}
            </div>

            <div class="border rounded p-3 bg-light-subtle">
              <div class="text-muted small mb-2">연결된 서버명</div>

              <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
                <div class="d-inline-flex align-items-center gap-2 px-3 py-2 rounded-pill server-pill-light">
                  <span class="server-dot" :class="{ muted: !discordGuild }"></span>
                  <span class="fw-semibold">
                    {{ discordGuild?.name ?? '연결된 서버 없음' }}
                  </span>
                </div>

                <button
                  type="button"
                  class="btn btn-discord"
                  :disabled="discordLoadingConnect"
                  @click="startDiscordServerConnect"
                >
                  <i class="bi bi-discord me-2"></i>
                  Discord 서버 변경하기
                </button>
              </div>

              <div class="text-muted small mt-3" style="line-height: 1.4">
                Discord 서버 연결을 통해 일정 관련 알림을 받을 수 있습니다.<br />
                - 공개장 또는 서버 공개장만 변경할 수 있습니다.
              </div>

              <!-- 알림 채널 -->
              <div class="mt-3">
                <div class="text-muted small mb-2">알림 채널</div>

                <div v-if="!discordGuild" class="text-muted small">
                  서버를 먼저 연결해 주세요.
                </div>

                <div v-else>
                  <select
                    class="form-select"
                    :disabled="discordLoadingChannels || discordChannels.length === 0"
                    :value="discordSelectedChannelId ?? ''"
                    @change="onChangeDiscordChannel"
                  >
                    <option value="" disabled>
                      {{ discordLoadingChannels ? '채널 불러오는 중...' : '채널을 선택하세요' }}
                    </option>
                    <option v-for="c in discordChannels" :key="c.id" :value="c.id">
                      # {{ c.name }}
                    </option>
                  </select>

                  <div v-if="discordSaveStatus === 'saving'" class="text-muted small mt-2">
                    반영 중...
                  </div>
                  <div v-else-if="discordSaveStatus === 'saved'" class="text-success small mt-2">
                    반영 완료
                  </div>
                  <div v-else-if="discordSaveStatus === 'error'" class="text-danger small mt-2">
                    반영 실패 (잠시 후 다시 시도)
                  </div>

                  <div v-if="discordChannelsError" class="alert alert-danger py-2 small mt-2 mb-0">
                    {{ discordChannelsError }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- (리더 전용) 멤버 관리 ... (원래 코드 유지) -->
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
                    <template v-if="m.role === 'leader'">
                      <span class="badge bg-primary-subtle text-primary">리더</span>
                    </template>

                    <template v-else>
                      <select class="form-select form-select-sm w-auto" :value="m.role" @change="onRoleChange(m.id, $event)">
                        <option value="admin">관리자</option>
                        <option value="member">멤버</option>
                      </select>

                      <button type="button" class="btn btn-outline-danger btn-sm" @click="$emit('kick', m.id)">
                        추방
                      </button>
                    </template>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- 3) 스터디 나가기 -->
          <div class="mb-3 border rounded p-3 bg-light-subtle">
            <h6 class="fw-semibold mb-2">스터디 나가기</h6>
            <p class="text-muted small mb-3">
              스터디를 나가면 더 이상 일정, 공지, 시험에 접근할 수 없습니다.
            </p>

            <div class="d-flex justify-content-end align-items-center gap-2">
              <span v-if="myRole === 'leader'" class="text-danger small me-auto">
                리더는 스터디를 해산해야만 나갈 수 있습니다.
              </span>

              <button type="button" class="btn btn-danger btn-sm" :disabled="myRole === 'leader'" @click="$emit('leave')">
                스터디 나가기
              </button>
            </div>
          </div>

          <!-- 4) (리더 전용) 스터디 해산 -->
          <div v-if="isLeader" class="border rounded p-3 danger-section mb-2">
            <h6 class="fw-semibold mb-2 text-danger d-flex align-items-center gap-1">
              <i class="bi bi-exclamation-triangle-fill"></i>
              스터디 해산
            </h6>
            <p class="text-muted small mb-3">
              스터디를 해산하면 일정, 공지사항, 시험 등 모든 데이터가 삭제되며 복구할 수 없습니다.
            </p>
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-outline-danger btn-sm" @click="$emit('dissolve')">
                스터디 해산
              </button>
            </div>
          </div>

          <!-- 닫기 -->
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
import { ref, computed, watch } from 'vue'
import client from '@/api/client'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'

type StudyRole = 'leader' | 'admin' | 'member'

interface StudyMember {
  id: number
  username: string
  email: string
  profile_img: string | null
  role: StudyRole
}

type DiscordSaveStatus = 'idle' | 'saving' | 'saved' | 'error'

/** ✅ GET /studies/<study>/discord/get_connected_guild/ 응답 */
interface ConnectedGuildResponse {
  study: {
    leader: number
    created_at: string
  }
  guild: {
    id: number
    name: string
    icon_url: string | null
    is_active: boolean
  }
  channel: {
    id: number
    name: string
    is_active: boolean
    guild: number
  } | null
}

/** ✅ GET /studies/<study_id>/discord/<guild_id>/fetch_guild_channel/ 응답 */
interface FetchGuildChannelResponse {
  guild: {
    id: number
    name: string
  }
  channels: Array<{
    id: number
    name: string
  }>
}

/** 템플릿 유지용 */
interface ConnectedGuild {
  id: string
  name: string
  notify_channel_id?: string | null
}

interface DiscordChannel {
  id: string
  name: string
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

/* ---------------- 기존 로직 ---------------- */
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

/* ---------------- ✅ Discord 연동 ---------------- */
const discordGuild = ref<ConnectedGuild | null>(null)
const discordChannels = ref<DiscordChannel[]>([])
const discordSelectedChannelId = ref<string | null>(null)

const discordLoadingConnect = ref(false)
const discordLoadingChannels = ref(false)
const discordSaveStatus = ref<DiscordSaveStatus>('idle')

const discordError = ref('')
const discordChannelsError = ref('')

/* ---------------- ✅ pending studyId 저장 (sessionStorage) ---------------- */
const DISCORD_PENDING_KEY = 'nestudy-discord-pending'
type PendingDiscord = { studyId: number; createdAt: number }

function saveDiscordPending(studyId: number) {
  const pending: PendingDiscord = { studyId, createdAt: Date.now() }
  sessionStorage.setItem(DISCORD_PENDING_KEY, JSON.stringify(pending))
}

/** 1) 연동된 서버/채널 조회 */
async function fetchDiscordGuild() {
  discordError.value = ''
  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')

  const res = await client.get<ConnectedGuildResponse>(
    `${API_BASE}/studies/${props.studyId}/discord/get_connected_guild/`,
    {
      withCredentials: true,
      headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
    },
  )

  const data = res.data

  // guild가 없으면 미연동 취급
  if (!data?.guild) {
    discordGuild.value = null
    discordSelectedChannelId.value = null
    return
  }

  discordGuild.value = {
    id: String(data.guild.id),
    name: data.guild.name,
    notify_channel_id: data.channel ? String(data.channel.id) : null,
  }

  discordSelectedChannelId.value = discordGuild.value.notify_channel_id ?? null
}

/** 2) 서버 채널 목록 조회 */
async function fetchDiscordChannels() {
  discordChannelsError.value = ''
  discordChannels.value = []
  if (!discordGuild.value) return

  discordLoadingChannels.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const res = await client.get<FetchGuildChannelResponse>(
      `${API_BASE}/studies/${props.studyId}/discord/${discordGuild.value.id}/fetch_guild_channel/`,
      {
        withCredentials: true,
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
      },
    )
    discordChannels.value = res.data.channels.map((c) => ({
      id: String(c.id),
      name: c.name,
    }))
  } catch (e: any) {
    console.error(e)
    discordChannelsError.value =
      e?.response?.data?.detail ?? '채널 목록을 불러오지 못했습니다.'
  } finally {
    discordLoadingChannels.value = false
  }
}

/** 3) 봇 초대 링크 */
async function startDiscordServerConnect() {
  discordLoadingConnect.value = true
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // ✅ 초대 시작 시점에 studyId 저장
    saveDiscordPending(props.studyId)

    const res = await client.get<{ url: string }>(`${API_BASE}/discord/bot/invite/`, {
      withCredentials: true,
      headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
    })

    window.location.href = res.data.url
  } catch (e: any) {
    console.error(e)
    discordError.value =
      e?.response?.data?.detail ?? '디스코드 봇 초대를 시작하지 못했습니다.'
  } finally {
    discordLoadingConnect.value = false
  }
}

/** 4) 선택한 채널을 스터디와 연결 */
async function patchDiscordNotifyChannel(channelId: string) {
  discordSaveStatus.value = 'saving'
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.post(
      `${API_BASE}/studies/${props.studyId}/discord/connect_channel/`,
      { channel_id: channelId },
      {
        withCredentials: true,
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : undefined,
      },
    )

    discordSelectedChannelId.value = channelId
    if (discordGuild.value) discordGuild.value.notify_channel_id = channelId

    discordSaveStatus.value = 'saved'
    setTimeout(() => {
      if (discordSaveStatus.value === 'saved') discordSaveStatus.value = 'idle'
    }, 900)
  } catch (e) {
    console.error(e)
    discordSaveStatus.value = 'error'
  }
}

function onChangeDiscordChannel(e: Event) {
  const target = e.target as HTMLSelectElement
  const channelId = target.value
  if (!channelId) return
  patchDiscordNotifyChannel(channelId)
}

/** ✅ 모달 열릴 때마다 최신화 */
watch(
  () => props.show,
  async (v) => {
    if (!v) return
    await fetchDiscordGuild()
    if (discordGuild.value) await fetchDiscordChannels()
  },
  { immediate: true },
)
</script>

<style scoped>
/* (스타일은 이전 그대로) */
.modal-header-custom {
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e5e9f0;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

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

.study-manage-modal {
  width: 100%;
  max-width: 760px;
  margin: 0 1.25rem;
}

.study-manage-modal .card {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  border: 1px solid #dee3ea;
}

.study-manage-modal .card-body {
  padding: 1.5rem !important;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .study-manage-modal {
    max-width: 100%;
    margin: 0 1rem;
  }
}

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

.info-row + .info-row {
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

.study-code-box {
  min-width: 96px;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1px dashed #cbd5e1;
  background-color: #ffffff;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
    'Courier New', monospace;
  letter-spacing: 0.08em;
  text-align: center;
  font-size: 0.8rem;
  color: #0f172a;
}

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

.member-list-group {
  border-radius: 12px;
}
.member-list-item {
  padding-top: 0.55rem;
  padding-bottom: 0.55rem;
}

.danger-section {
  background-color: #fff5f5;
}

.server-pill-light {
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.server-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #5865f2;
}
.server-dot.muted {
  background: rgba(100, 116, 139, 0.35);
}

.btn-discord {
  background: #5865f2;
  border: 1px solid #5865f2;
  color: #fff;
  font-weight: 700;
  border-radius: 10px;
  padding: 10px 14px;
}
.btn-discord:hover {
  background-color: #4752c4;
  border-color: #4752c4;
  color: #fff;
}
.btn-discord:disabled {
  opacity: 0.65;
}
</style>
