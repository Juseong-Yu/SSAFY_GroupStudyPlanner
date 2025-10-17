// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Bootstrap 5
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)

// ✅ Pinia 전역 등록 (필수)
const pinia = createPinia()
app.use(pinia)

// ✅ Router 등록
app.use(router)

// ✅ 단 한 번만 mount
app.mount('#app')
