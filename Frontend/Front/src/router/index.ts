import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import SignUpPage from '../views/accounts/SignUpPage.vue'
import LoginPage from '@/views/accounts/LoginPage.vue'
import MainPage from '@/views/MainPage.vue'
import PasswordCheckPage from '@/views/accounts/PasswordCheckPage.vue'
import ProfileUpdatePage from '@/views/accounts/ProfileUpdatePage.vue'

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
      component: MainPage
    },
    {
    path: '/accounts/password-check',
    name: 'PasswordCheck',
    component: PasswordCheckPage,
  },
  {
    path: '/accounts/update',
    name: 'ProfileUpdate',
    component: ProfileUpdatePage,
  },
  ],
})

export default router
