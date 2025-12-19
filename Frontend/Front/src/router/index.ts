import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import SignUpPage from '../views/accounts/SignUpPage.vue'
import LoginPage from '@/views/accounts/LoginPage.vue'
import MainPage from '@/views/MainPage.vue'
import PasswordCheckPage from '@/views/accounts/PasswordCheckPage.vue'
import ProfileUpdatePage from '@/views/settings/ProfileUpdatePage.vue'
import ProfilePage from '@/views/settings/ProfilePage.vue'
import StudyPage from '@/views/studies/StudyPage.vue'
import StudyNoticePage from '@/views/studies/notice/StudyNoticePage.vue'
import NoticeCreatePage from '@/views/studies/notice/NoticeCreatePage.vue'
import NoticeDetailPage from '@/views/studies/notice/NoticeDetailPage.vue'
import NoticeEditPage from '@/views/studies/notice/NoticeEditPage.vue'
import SchedulePage from '@/views/studies/schedule/SchedulePage.vue'
import StudyExamsPage from '@/views/studies/exams/StudyExamsPage.vue'
import ExamEditorPage from '@/views/studies/exams/ExamEditorPage.vue'
import ExamTakePage from '@/views/studies/exams/ExamTakePage.vue'
import ConnectPage from '@/views/settings/ConnectPage.vue'


// 🔥 스터디 역할 스토어
import { useStudyRoleStore } from '@/stores/studyRoleStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'LandingPage',
      component: LandingPage,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpPage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/main',
      name: 'main',
      component: MainPage,
    },
    {
      path: '/accounts/password-check',
      name: 'PasswordCheck',
      component: PasswordCheckPage,
    },
    {
      path: '/settings/profile',
      name: 'Profile',
      component: ProfilePage,
    },
    {
      path: '/settings/update',
      name: 'ProfileUpdate',
      component: ProfileUpdatePage,
    },
    {
      path: '/settings/connect',
      name: 'Connect',
      component: ConnectPage,
    },
    {
      path: '/api/auth/discord/callback', // ✅ 추천
      name: 'DiscordCallback',
      component: () => import('@/views/auth/DiscordCallbackView.vue'),
    },
    {
      path: '/api/auth/discord/login/callback', // ✅ 추천
      name: 'DiscordLog',
      component: () => import('@/views/auth/DiscordLoginView.vue'),
    },
    {
      path: '/accounts/OauthInfo',
      name: 'OauthInfo',
      component: () => import('@/views/accounts/OauthExtraInfoView.vue'),
    },
    {
    path: '/discord/connect',
    name: 'DiscordConnect',
    component: () => import('@/views/auth/DiscordConnectView.vue'),
    },

    // ===== 스터디 관련 라우트들 (모두 role 필요) =====
    {
      path: '/studies/:id',
      name: 'Study',
      component: StudyPage,
      meta: {
        requiresStudyRole: true,
      },
    },
    
    {
      path: '/studies/:id/notice',
      name: 'NoticeMain',
      component: StudyNoticePage,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:id/notice/create',
      name: 'NoticeCreate',
      component: NoticeCreatePage,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:id/notice/:noticeId',
      name: 'NoticeDetail',
      component: NoticeDetailPage,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:id/notice/:noticeId/edit',
      name: 'NoticeEdit',
      component: NoticeEditPage,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:id/schedule/',
      name: 'ScheduleMain',
      component: SchedulePage,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:studyId/exams',
      name: 'StudyExams',
      component: StudyExamsPage,
      props: true,
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:studyId/exams/new',
      name: 'ExamCreate',
      component: ExamEditorPage,
      props: route => ({
        studyId: Number(route.params.studyId),
        mode: (route.query.mode as 'manual' | 'ai') || 'manual',
        questionCount: route.query.questionCount
          ? Number(route.query.questionCount)
          : 5,
        visibility:
          (route.query.visibility as 'public' | 'score_only' | 'private') ||
          'public',
        openDate: (route.query.openDate as string) || null,
        dueDate: (route.query.dueDate as string) || null,
        draftId: route.query.draftId ? Number(route.query.draftId) : null,
      }),
      meta: {
        requiresStudyRole: true,
      },
    },
    {
      path: '/studies/:studyId/exams/:examId',
      name: 'ExamTake',
      component: ExamTakePage,
      meta: {
        requiresStudyRole: true,
      },
    },
  ],
})

/**
 * 🔥 전역 라우터 가드
 * - /studies/... 로 가는 모든 라우트는 진입 전에 get_my_role 호출 (캐시 없을 때만)
 * - 403/404 등은 여기서 처리
 */
router.beforeEach(async (to, from, next) => {
  const needsStudyRole = to.matched.some(
    record => record.meta && record.meta.requiresStudyRole,
  )

  if (!needsStudyRole) {
    return next()
  }

  // studyId 파라미터 이름이 라우트마다 다를 수 있으니 둘 다 체크
  const rawStudyId = (to.params.studyId ?? to.params.id) as
    | string
    | string[]
    | undefined

  if (!rawStudyId) {
    console.warn(
      'requiresStudyRole인데 studyId/id 파라미터가 없습니다:',
      to.fullPath,
    )
    return next({ name: 'main' })
  }

  const studyId =
    typeof rawStudyId === 'string' ? rawStudyId : rawStudyId[0] || ''

  const roleStore = useStudyRoleStore()
  const cached = roleStore.getRoleInfo(studyId)

  if (cached) {
    // 이미 캐시된 역할이 있으면 그냥 통과
    roleStore.currentStudyId = studyId
    return next()
  }

  // 캐시 없으면 API 호출
  const result = await roleStore.fetchMyRole(studyId)

  if (result.ok) {
    return next()
  }

  // 실패한 경우: 상태코드에 따라 분기 (간단 버전)
  if (result.status === 403) {
    alert('이 스터디에 접근할 권한이 없습니다.')
    return next({ name: 'main' })
  }

  if (result.status === 404) {
    alert('존재하지 않는 스터디입니다.')
    return next({ name: 'main' })
  }

  alert(result.error || '스터디 접근 중 오류가 발생했습니다.')
  return next({ name: 'main' })
})

export default router
