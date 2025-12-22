<!-- src/views/StudyPage.vue -->
<template>
  <AppShell>
    <!-- ✅ 양쪽 여백 맞추기: 전체를 한 번 더 감싸서 max-width + 중앙 정렬 -->
    <div class="container-fluid py-4 d-flex justify-content-center">
      <div class="w-100 study-page-wrapper">
        <!-- 상단: 제목 + 참여 코드 + 스터디 관리 버튼 -->
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h2 class="fw-bold mb-3">{{ studyTitle }}</h2>
          </div>

          <button
            type="button"
            class="btn btn-light-outline btn-sm d-flex align-items-center justify-content-center"
            @click="openManageModal"
            aria-label="스터디 관리"
            title="스터디 관리"
          >
            <!-- 사람 + 설정 느낌 -->
            <i class="bi bi-gear"></i>
          </button>
        </div>

        <div class="row g-4">
          <!-- 왼쪽: 달력 -->
          <div class="col-12 col-xl-8">
            <BaseScheduleCalendar
              ref="calendarComponentRef"
              :events="calendarEvents"
              :loading="!isLoaded && !calendarEvents.length"
              @event-click="handleEventClick"
            />
          </div>

          <!-- 오른쪽: 공지사항 + 시험 + 일정 -->
          <div class="col-12 col-xl-4">
            <div class="right-stack sticky-xl-top" style="top: 88px">
              <!-- ✅ 공지사항 -->
              <div class="card mb-3 shadow-sm">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <span class="fw-semibold">공지사항</span>
                  <RouterLink
                    :to="{ name: 'NoticeMain', params: { id: studyId } }"
                    class="header-link"
                  >
                    ->
                  </RouterLink>
                </div>

                <div class="list-group list-group-flush">
                  <!-- 최근 2개 -->
                  <RouterLink
                    v-for="n in topNotices"
                    :key="n.id"
                    :to="`/studies/${studyId}/notice/${n.id}`"
                    class="list-group-item py-3 text-reset text-decoration-none notice-link"
                  >
                    <div class="fw-semibold text-truncate mb-1">
                      {{ n.title }}
                    </div>

                    <div class="d-flex align-items-center text-muted small">
                      <img
                        v-if="n.author.profileImg"
                        :src="n.author.profileImg"
                        alt="avatar"
                        class="avatar me-2"
                        referrerpolicy="no-referrer"
                      />
                      <div v-else class="avatar avatar-fallback me-2">
                        <i class="bi bi-person-fill text-secondary" aria-hidden="true"></i>
                      </div>

                      <span class="me-2 fw-semibold">{{ n.author.username }}</span>
                      <span aria-hidden="true" class="mx-1">·</span>
                      <time class="text-muted" :datetime="n.createdAt">
                        {{ formatDate(n.createdAt) }}
                      </time>
                    </div>
                  </RouterLink>

                  <div
                    v-if="!topNotices.length && isLoaded"
                    class="list-group-item py-4 text-center text-muted small"
                  >
                    아직 등록된 공지사항이 없어요.
                  </div>
                </div>
              </div>

              <!-- ✅ 시험 카드 -->
              <div class="card mb-3 shadow-sm">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <span class="fw-semibold">시험</span>
                  <RouterLink
                    :to="{ name: 'StudyExams', params: { studyId: studyId } }"
                    class="header-link"
                  >
                    ->
                  </RouterLink>
                </div>

                <div class="list-group list-group-flush">
                  <!-- 가까운 시험 최대 2개 -->
                  <RouterLink
                    v-for="exam in upcomingExams"
                    :key="exam.id"
                    :to="{ name: 'StudyExams', params: { studyId: studyId } }"
                    class="list-group-item py-3 text-reset text-decoration-none notice-link"
                  >
                    <div class="fw-semibold text-truncate mb-1">
                      {{ exam.title }}
                    </div>

                    <div class="d-flex flex-wrap align-items-center gap-2 small text-muted">
                      <span>
                        {{ formatExamDue(exam.due_at) }}
                      </span>

                      <span class="badge bg-secondary-subtle text-secondary">
                        {{ visibilityLabelMap[exam.visibility] }}
                      </span>

                      <span
                        :class="
                          exam.has_taken
                            ? 'badge bg-success-subtle text-success'
                            : 'badge bg-primary-subtle text-primary'
                        "
                      >
                        {{ exam.has_taken ? '응시 완료' : '미응시' }}
                      </span>
                    </div>
                  </RouterLink>

                  <div
                    v-if="!upcomingExams.length && isLoaded"
                    class="list-group-item py-4 text-center text-muted small"
                  >
                    아직 예정된 시험이 없어요.
                  </div>
                </div>
              </div>

              <!-- ✅ 일정 카드 -->
              <div class="card shadow-sm">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <span class="fw-semibold">일정</span>
                  <RouterLink
                    :to="{ name: 'ScheduleMain', params: { id: studyId } }"
                    class="header-link"
                  >
                    ->
                  </RouterLink>
                </div>

                <div class="list-group list-group-flush">
                  <div
                    class="list-group-item py-3 list-item-clickable"
                    v-for="s in upcomingSchedules"
                    :key="s.id"
                    @click="openDetailModal(s.id)"
                  >
                    <div class="fw-semibold text-truncate">
                      <i class="bi bi-calendar-event me-1 text-primary"></i>
                      {{ s.schedule.title }}
                    </div>
                    <div class="text-muted small">
                      {{ formatScheduleRange(s.schedule.start_at, s.schedule.end_at) }}
                    </div>
                  </div>

                  <div
                    v-if="!upcomingSchedules.length && isLoaded"
                    class="list-group-item py-4 text-center text-muted small"
                  >
                    아직 등록된 스터디 일정이 없어요.
                  </div>
                </div>
              </div>
            </div>
            <!-- /right-stack -->
          </div>
        </div>
      </div>
    </div>

    <!-- 일정 상세 모달 -->
    <ScheduleDetailModal
      :show="showDetailModal"
      :error="detailError"
      :detail="detail"
      :user-role="myScheduleRole"
      @close="closeDetailModal"
      @delete="handleDetailDelete"
      @edit="handleDetailEdit"
    />

    <!-- 스터디 관리 모달 -->
    <StudyManageModal
      :show="showManageModal"
      :isLeader="isLeader"
      :myRole="myRole"
      :studyId="studyId"
      :studyTitle="studyTitle"
      :members="members"
      :loadingMembers="loadingMembers"
      :membersError="membersError"
      :joinCode="joinCode"
      :joinCodeLoading="joinCodeLoading"
      :joinCodeError="joinCodeError"
      @close="handleCloseManageModal"
      @leave="handleLeaveStudy"
      @dissolve="handleDissolveStudy"
      @kick="handleKickMember"
      @change-role="handleChangeRole"
    />
  </AppShell>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import client from '@/api/client'
import AppShell from '@/layouts/AppShell.vue'
import BaseScheduleCalendar from '@/components/BaseScheduleCalendar.vue'
import ScheduleDetailModal from '@/components/ScheduleDetailModal.vue'
import StudyManageModal from '@/views/studies/components/StudyManageModal.vue'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import type { EventInput, EventClickArg } from '@fullcalendar/core'
import { useStudyRoleStore, type StudyRole } from '@/stores/studyRoleStore'
import { useUiStore } from '@/stores/ui'
import { useStudiesStore } from '@/stores/studies'
// 백엔드 베이스 URL
const API_BASE = import.meta.env.VITE_API_BASE_URL as string

const route = useRoute()
const router = useRouter()
const studyRoleStore = useStudyRoleStore()
const calendarComponentRef = ref<any>(null)
const uiStore = useUiStore()
const studiesStroe = useStudiesStore()
// 🔗 스터디 기본 정보
const studyId = computed(() => Number(route.params.id))
const studyTitle = ref('스터디 불러오는 중...')
const studyLeader = ref<string | null>(null)
const joinedAt = ref<string | null>(null)
const createdAt = ref<string | null>(null)
const joinCode = ref<string | null>(null)

const joinCodeLoading = ref(false)
const joinCodeError = ref('')
const isLoaded = ref(false)

/* =========================
 *   공지사항 타입 / 상태
 * ========================= */

interface ApiNotice {
  id: number
  title: string
  created_at: string
  updated_at: string
  study_id: number
  author: {
    id: number
    username: string
    email: string
    profile_img: string | null
  }
}

type Notice = {
  id: number
  title: string
  createdAt: string
  author: {
    id: number
    username: string
    email: string
    profileImg: string | null
  }
}

const notices = ref<Notice[]>([])

const topNotices = computed(() =>
  [...notices.value]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 2),
)

/* =========================
 *   일정 타입 / 상태
 * ========================= */

interface StudyScheduleItem {
  id: number
  schedule: {
    id: number
    title: string
    description: string
    start_at: string
    end_at: string
  }
  author: {
    id: number
    username: string
    email: string
    profile_img: string | null
  }
  study: {
    id: number
    name: string
  }
}

const schedules = ref<StudyScheduleItem[]>([])
const calendarEvents = ref<EventInput[]>([])

/* =========================
 *   일정 상세 타입 / 상태
 * ========================= */

type ScheduleType = 'study' | 'personal'

interface ScheduleAuthor {
  id: number
  username: string
  email: string
  profile_img: string | null
}

interface ScheduleStudy {
  id: number
  name: string
}

interface CombinedScheduleCore {
  title: string
  description: string
  start_at: string
  end_at?: string | null
}

interface CombinedData {
  id: number
  schedule: CombinedScheduleCore
  author?: ScheduleAuthor
  study?: ScheduleStudy
  [key: string]: any
}

interface StoredEvent {
  type: ScheduleType
  data: CombinedData
}

interface ScheduleDetailApi {
  id: number
  schedule: {
    title: string
    description: string
    start_at: string
    end_at: string | null
  }
  author: ScheduleAuthor
  study: ScheduleStudy
}

const showDetailModal = ref(false)
const detailError = ref('')
const detail = ref<StoredEvent | null>(null)

/* =========================
 *   시험 타입 / 상태
 * ========================= */

type VisibilityType = 'public' | 'score_only' | 'private'

interface ExamListItem {
  id: number
  title: string
  due_at: string | null
  visibility: VisibilityType
  has_taken: boolean
}

const exams = ref<ExamListItem[]>([])

const visibilityLabelMap: Record<VisibilityType, string> = {
  public: '전체 공개',
  score_only: '점수만 공개',
  private: '비공개',
}

/* =========================
 *   스터디 멤버 / 역할 / 관리 모달 상태
 * ========================= */

interface StudyMember {
  id: number
  username: string
  email: string
  profile_img: string | null
  role: StudyRole
}

const showManageModal = ref(false)
const members = ref<StudyMember[]>([])
const loadingMembers = ref(false)
const membersError = ref('')

// store 기반 내 역할
const myRole = computed<StudyRole>(() => {
  const id = studyId.value
  if (!id) return 'member'
  return studyRoleStore.getRole(id) ?? 'member'
})

const isLeader = computed(() => {
  const id = studyId.value
  if (!id) return false
  return studyRoleStore.isLeader(id)
})

/** ✅ 모달에 내려줄 역할 (admin/leader만 수정·삭제 버튼 노출) */
const myScheduleRole = computed(() => myRole.value)

/* =========================
 *   API 호출 함수들
 * ========================= */

async function fetchStudy() {
  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const { data } = await client.get(`${API_BASE}/studies/${studyId.value}/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken || '',
      },
    })

    studyTitle.value = data.name ?? '이름 없는 스터디'
    studyLeader.value = data.leader ?? null
    joinedAt.value = data.joined_at ?? null
    createdAt.value = data.created_at ?? null
  } catch (error) {
    console.error('스터디 조회 실패:', error)
    studyTitle.value = '스터디 정보를 불러오지 못했어요'
  }
}

async function fetchJoinCode() {
  if (!studyId.value) return
  joinCodeLoading.value = true
  joinCodeError.value = ''

  try {
    if (isLeader.value) {
      await ensureCsrf()
      const { data } = await client.get<{ join_code: string }>(
        `${API_BASE}/studies/${studyId.value}/join_code/`,
        { withCredentials: true },
      )
      joinCode.value = data.join_code ?? null
    }
  } catch (e) {
    console.error('참여 코드 조회 실패:', e)
    joinCode.value = null
    joinCodeError.value = '참여 코드를 불러오지 못했습니다.'
  } finally {
    joinCodeLoading.value = false
  }
}

async function fetchSchedules() {
  try {
    await ensureCsrf()

    const { data } = await client.get<StudyScheduleItem[]>(
      `${API_BASE}/studies/${studyId.value}/schedules/study_schedule_list/`,
      {
        withCredentials: true,
      },
    )

    schedules.value = data

    const events: EventInput[] = data.map((item) => {
      const start = new Date(item.schedule.start_at)
      const end = new Date(item.schedule.end_at)

      if (
        end.getHours() === 0 &&
        end.getMinutes() === 0 &&
        end.getSeconds() === 0 &&
        end.getMilliseconds() === 0
      ) {
        end.setTime(end.getTime() - 1)
      }

      return {
        id: String(item.id),
        title: item.schedule.title,
        start,
        end,
        backgroundColor: '#e4edff',
        borderColor: '#a7c4ff',
        textColor: '#111827',
      }
    })

    calendarEvents.value = events
  } catch (error) {
    console.error('일정 목록 조회 실패:', error)
    schedules.value = []
    calendarEvents.value = []
  }
}

async function fetchNotices() {
  try {
    await ensureCsrf()

    const { data } = await client.get<ApiNotice[]>(
      `${API_BASE}/studies/${studyId.value}/posts/notice_list/`,
      {
        withCredentials: true,
      },
    )

    notices.value = data.map((n) => ({
      id: n.id,
      title: n.title,
      createdAt: n.created_at,
      author: {
        id: n.author.id,
        username: n.author.username,
        email: n.author.email,
        profileImg: n.author.profile_img ? `${API_BASE}${n.author.profile_img}` : null,
      },
    }))
  } catch (error) {
    console.error('공지사항 목록 조회 실패:', error)
    notices.value = []
  }
}

async function fetchExams() {
  try {
    await ensureCsrf()

    const { data } = await client.get<any[]>(`${API_BASE}/studies/${studyId.value}/exams/`, {
      withCredentials: true,
    })

    exams.value = data.map((exam) => ({
      id: exam.id,
      title: exam.title,
      due_at: exam.due_at,
      visibility: exam.visibility as VisibilityType,
      has_taken: Boolean(exam.has_taken),
    }))
  } catch (error) {
    console.error('시험 목록 조회 실패:', error)
    exams.value = []
  }
}

async function fetchMembers() {
  if (!studyId.value) return
  loadingMembers.value = true
  membersError.value = ''

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    const { data } = await client.get<any[]>(`${API_BASE}/studies/${studyId.value}/member_list/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken || '',
      },
    })

    members.value = data.map((item) => ({
      id: item.user.id,
      username: item.user.username,
      email: item.user.email,
      profile_img: null,
      role: item.role as StudyRole,
    }))
  } catch (e) {
    console.error('멤버 목록 조회 실패:', e)
    membersError.value = '멤버 목록을 불러오지 못했습니다.'
    members.value = []
  } finally {
    loadingMembers.value = false
  }
}

/* =========================
 *   유틸 함수들
 * ========================= */

function formatDate(iso: string) {
  const d = new Date(iso)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}.${mm}.${dd}`
}

function formatScheduleRange(startIso: string, endIso: string) {
  const start = new Date(startIso)
  const end = new Date(endIso)

  const startDate = `${start.getMonth() + 1}/${start.getDate()}`
  const startTime = `${String(start.getHours()).padStart(2, '0')}:${String(
    start.getMinutes(),
  ).padStart(2, '0')}`

  const endDate = `${end.getMonth() + 1}/${end.getDate()}`
  const endTime = `${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(
    2,
    '0',
  )}`

  if (startDate === endDate) {
    return `${startDate} ${startTime} ~ ${endTime}`
  }
  return `${startDate} ${startTime} ~ ${endDate} ${endTime}`
}

function formatExamDue(iso: string | null) {
  if (!iso) return '마감 없음'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '마감 없음'
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `마감: ${yyyy}.${mm}.${dd} ${hh}:${mi}`
}

/* =========================
 *   오른쪽 카드 계산 값
 * ========================= */

const today = new Date()
today.setHours(0, 0, 0, 0)

const upcomingSchedules = computed(() =>
  schedules.value
    .filter((item) => {
      const end = new Date(item.schedule.end_at)
      return end.getTime() >= today.getTime()
    })
    .sort(
      (a, b) => new Date(a.schedule.start_at).getTime() - new Date(b.schedule.start_at).getTime(),
    )
    .slice(0, 2),
)

const upcomingExams = computed(() =>
  exams.value
    .filter((exam) => {
      if (!exam.due_at) return true
      const due = new Date(exam.due_at)
      return due.getTime() >= today.getTime()
    })
    .sort((a, b) => {
      if (!a.due_at && !b.due_at) return 0
      if (!a.due_at) return 1
      if (!b.due_at) return -1
      return new Date(a.due_at).getTime() - new Date(b.due_at).getTime()
    })
    .slice(0, 2),
)

/* =========================
 *   일정 상세 모달 관련
 * ========================= */

async function openDetailModal(id: number) {
  if (!studyId.value) return
  showDetailModal.value = true
  detailError.value = ''
  detail.value = null

  try {
    await ensureCsrf()
    const { data } = await client.get<ScheduleDetailApi>(
      `${API_BASE}/studies/${studyId.value}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
      },
    )

    detail.value = {
      type: 'study',
      data: {
        id: data.id,
        schedule: {
          title: data.schedule.title,
          description: data.schedule.description,
          start_at: data.schedule.start_at,
          end_at: data.schedule.end_at,
        },
        author: data.author,
        study: data.study,
      },
    }
  } catch (e) {
    console.error(e)
    detailError.value = '일정 정보를 불러오지 못했습니다.'
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  detail.value = null
  detailError.value = ''
}

const handleEventClick = (info: EventClickArg) => {
  const id = Number(info.event.id)
  if (!Number.isNaN(id)) {
    openDetailModal(id)
  }
}

/** ✅ admin 이상일 때만 의미 있게 동작하는 삭제 핸들러 */
async function handleDetailDelete(id: number) {
  if (myRole.value === 'member') {
    alert('일정 삭제 권한이 없습니다.')
    return
  }
  if (!studyId.value) return

  const ok = window.confirm('이 일정을 삭제하시겠습니까?')
  if (!ok) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.delete(
      `${API_BASE}/studies/${studyId.value}/schedules/${id}/study_schedule_detail/`,
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
        },
      },
    )

    await fetchSchedules()
    closeDetailModal()
  } catch (e) {
    console.error('일정 삭제 실패:', e)
    alert('일정 삭제 중 오류가 발생했습니다.')
  }
}

/** ✅ 수정 버튼: 일단 스터디 일정 페이지로 라우팅 (거기서 수정 모달 열도록 확장 가능) */
function handleDetailEdit(payload: StoredEvent) {
  if (myRole.value === 'member') {
    alert('일정 수정 권한이 없습니다.')
    return
  }
  if (!payload?.data?.id || !studyId.value) return

  // 나중에 SchedulePage에서 `query.editId` 읽어서 바로 수정 모달 열게 만들면 깔끔
  router.push({
    name: 'ScheduleMain',
    params: { id: studyId.value },
    query: { editId: String(payload.data.id) },
  })
}

/* =========================
 *   스터디 관리 모달 관련
 * ========================= */

function openManageModal() {
  showManageModal.value = true
  fetchMembers()
  fetchJoinCode()
}

function handleCloseManageModal() {
  showManageModal.value = false
}

async function handleLeaveStudy() {
  if (myRole.value === 'leader') {
    alert('리더는 스터디를 해산해야만 나갈 수 있습니다.')
    return
  }
  if (!studyId.value) return

  const ok = window.confirm('정말 이 스터디에서 탈퇴하시겠습니까?')
  if (!ok) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    // 🔥 실제 "나가기" 엔드포인트로 수정 필요
    await client.post(
      `${API_BASE}/studies/leave/`,
      {
        id: studyId.value,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
        },
      },
    )

    alert('스터디에서 탈퇴되었습니다.')
    studiesStroe.refresh()
    router.push('/main')
  } catch (e) {
    console.error('스터디 탈퇴 실패:', e)
    alert('스터디 탈퇴 중 오류가 발생했습니다.')
  }
}

async function handleDissolveStudy() {
  if (!studyId.value) return

  const ok = window.confirm(
    '정말 이 스터디를 해산하시겠습니까?\n모든 일정, 공지, 시험 데이터가 삭제됩니다.',
  )
  if (!ok) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.delete(`${API_BASE}/studies/${studyId.value}/study_delete/`, {
      withCredentials: true,
      headers: {
        'X-CSRFToken': csrftoken || '',
      },
    })
    studiesStroe.refresh()
    alert('스터디가 해산되었습니다.')
    router.push('/main')
  } catch (e) {
    console.error('스터디 해산 실패:', e)
    alert('스터디 해산 중 오류가 발생했습니다.')
  }
}

async function handleKickMember(memberId: number) {
  if (!studyId.value) return
  const ok = window.confirm('이 멤버를 스터디에서 추방하시겠습니까?')
  if (!ok) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.put(
      `${API_BASE}/studies/${studyId.value}/${memberId}/expel_member/`,
      {},
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
        },
      },
    )

    members.value = members.value.filter((m) => m.id !== memberId)
  } catch (e) {
    console.error('멤버 추방 실패:', e)
    alert('멤버 추방 중 오류가 발생했습니다.')
  }
}

async function handleChangeRole(memberId: number, role: StudyRole) {
  if (!studyId.value) return

  try {
    await ensureCsrf()
    const csrftoken = getCookie('csrftoken')

    await client.put(
      `${API_BASE}/studies/${studyId.value}/change_role/`,
      {
        target_id: memberId,
        role,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrftoken || '',
        },
      },
    )

    const target = members.value.find((m) => m.id === memberId)
    if (target) {
      target.role = role
    }
  } catch (e) {
    console.error('역할 변경 실패:', e)
    alert('역할 변경 중 오류가 발생했습니다.')
  }
}

/* =========================
 *   스터디 ID 변경 감시
 * ========================= */
watch(
  () => uiStore.sidebarOpen,
  async () => {
    // DOM 반영 기다리고
    await nextTick()

    // 사이드바 transition 끝난 뒤
    window.setTimeout(() => {
      calendarComponentRef.value?.updateSize?.()
    }, 300) // ← AppShell sidebar transition 시간
  },
)

watch(
  studyId,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return
    isLoaded.value = false

    try {
      await studyRoleStore.fetchMyRole(newId)
      await fetchStudy()
      await fetchSchedules()
      await fetchNotices()
      await fetchExams()
    } finally {
      isLoaded.value = true
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.study-page-wrapper {
  width: 100%;
  max-width: 1300px;
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 768px) {
  .study-page-wrapper {
    max-width: 1300px;
    padding-left: 3rem;
    padding-right: 3rem;
  }
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-fallback {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  background: #e9eef7;
  color: #2b3a67;
}

.right-stack .card {
  border-radius: 0.5rem;
}

.right-stack .list-group-item {
  border: 0 !important;
}

.right-stack .list-group-item:last-child {
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

.notice-link:hover,
.list-item-clickable:hover {
  background-color: #f8fafc;
}

.list-item-clickable {
  cursor: pointer;
}

.header-link {
  font-size: 1.15rem;
  font-weight: 600;
  color: #64748b;
  text-decoration: none;
  transition: color 0.15s ease-in-out;
}

.header-link:hover {
  color: #1e293b;
}

.btn-light-outline {
  color: #475569;
  border-radius: 8px;
  transition: 0.2s ease;
}

.btn-light-outline:hover {
  color: #000000;
}
</style>
