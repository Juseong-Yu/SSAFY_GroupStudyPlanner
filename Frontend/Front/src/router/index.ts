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
      path: '/studies/:id/create',
      name: 'NoticeCreate',
      component: NoticeCreatePage,
    },
    {
      path: '/studies/:id/detail/:id',
      name: 'NoticeDetail',
      component: NoticeDetailPage,
    },
  ],
})

export default router
