// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Bootstrap 5
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import '@/assets/main.css'
import 'md-editor-v3/lib/preview.css'

const app = createApp(App)

// ✅ Pinia 전역 등록 (필수)
const pinia = createPinia()
app.use(pinia)

// ✅ Router 등록
app.use(router)

//  mount
app.mount('#app')
