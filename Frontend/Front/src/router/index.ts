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
      path: '/studies/:id',
      name: 'Study',
      component: StudyPage,
    },
    {
      path: '/studies/:id/notice',
      name: 'NoticeMain',
      component: StudyNoticePage,
    },
    {
      path: '/studies/:id/notice/create',
      name: 'NoticeCreate',
      component: NoticeCreatePage,
    },
    {
      path: '/studies/:id/notice/:noticeId',
      name: 'NoticeDetail',
      component: NoticeDetailPage,
    },
    {
      path: '/studies/:id/notice/:noticeId/edit',
      name: 'NoticeEdit',
      component: NoticeEditPage,
    },
    {
      path: '/studies/:id/schedule/',
      name: 'ScheduleMain',
      component: SchedulePage,
    },
    {
    path: '/studies/:studyId/exams',
    name: 'StudyExams',
    component: StudyExamsPage,
    props: true,
  },
  {
    path: '/studies/:studyId/exams/new',
    name: 'ExamCreate',
    component: ExamEditorPage,
    props: route => ({
      studyId: Number(route.params.studyId),
      mode: (route.query.mode as 'manual' | 'ai') || 'manual',
      questionCount: route.query.questionCount ? Number(route.query.questionCount) : 5,
      visibility: (route.query.visibility as 'public' | 'score_only' | 'private') || 'public',
      dueDate: (route.query.dueDate as string) || null,
      draftId: route.query.draftId ? Number(route.query.draftId) : null,
    }),
  },
  ],
})

export default router
