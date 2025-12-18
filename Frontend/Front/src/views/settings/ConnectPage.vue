<template>
  <div class="d-flex min-vh-100">
    <!-- ✅ 왼쪽: SettingNavBar -->
    <SettingNavBar />

    <!-- ✅ 오른쪽 -->
    <div class="flex-grow-1 bg-white p-5">
      <div class="container" style="max-width: 1000px">
        <h3 class="fw-bold mb-4">외부 서비스 연동</h3>

        <div class="card shadow-sm">
          <div class="card-body p-4">
            <!-- ===================== -->
            <!-- ✅ Discord (로그인 연동만) -->
            <!-- ===================== -->
            <div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
              <div class="d-flex align-items-center gap-3">
                <div
                  class="rounded-circle border d-flex align-items-center justify-content-center bg-light"
                  style="width: 56px; height: 56px"
                >
                  <i class="bi bi-discord" style="font-size: 1.7rem; color: #5865f2"></i>
                </div>

                <div>
                  <div class="d-flex align-items-center gap-2">
                    <h5 class="mb-0 fw-bold">Discord</h5>

                    <!-- ✅ 상태 배지: 연동 중 / 연동 안 됨 / 확인 불가 / 연동됨 -->
                    <span class="badge" :class="discordStatusBadgeClass">
                      {{ discordStatusLabel }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="d-flex gap-2">
                <!-- ✅ Discord: 브랜드 컬러 버튼 -->
                <button
                  v-if="!isDiscordConnected"
                  class="btn discord-btn d-flex align-items-center gap-2 "
                  type="button"
                  :disabled="discordLoading"
                  @click="startDiscordConnect"
                >
                  <span v-if="discordLoading" class="spinner-border spinner-border-sm text-light" />
                  <i v-else class="bi bi-discord"></i>
                  {{ discordLoading ? '연결 중...' : '디스코드 연결' }}
                </button>

                <button
                  v-else
                  class="btn btn-outline-danger d-flex align-items-center gap-2"
                  type="button"
                  :disabled="discordLoading"
                  @click="disconnectDiscord"
                >
                  <span v-if="discordLoading" class="spinner-border spinner-border-sm" />
                  <i v-else class="bi bi-x-circle"></i>
                  {{ discordLoading ? '해제 중...' : '연동 해제' }}
                </button>
              </div>
            </div>

            <hr class="my-4" />

            <!-- ===================== -->
            <!-- ✅ Google 연동 블록 (유지) -->
            <!-- ===================== -->
            <div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
              <div class="d-flex align-items-center gap-3">
                <div
                  class="rounded-circle border d-flex align-items-center justify-content-center bg-light"
                  style="width: 56px; height: 56px"
                >
                  <img
                    :src="googleLogoSrc"
                    alt="Google"
                    width="30"
                    height="30"
                    style="display: block"
                  />
                </div>

                <div>
                  <div class="d-flex align-items-center gap-2">
                    <h5 class="mb-0 fw-bold">Google</h5>

                    <span class="badge" :class="googleStatusBadgeClass">
                      {{ googleStatusLabel }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="d-flex gap-2">
                <button
                  v-if="!isGoogleConnected"
                  class="btn google-btn d-flex align-items-center gap-2"
                  type="button"
                  :disabled="googleLoading"
                  @click="startGoogleConnect"
                >
                  <span v-if="googleLoading" class="spinner-border spinner-border-sm text-secondary" />
                  <img
                    v-else
                    :src="googleLogoSrc"
                    alt="Google"
                    width="20"
                    height="20"
                    style="display: block"
                  />
                  {{ googleLoading ? '연결 중...' : 'Google로 계속하기' }}
                </button>

                <button
                  v-else
                  class="btn btn-outline-danger d-flex align-items-center gap-2"
                  type="button"
                  :disabled="googleLoading"
                  @click="disconnectGoogle"
                >
                  <span v-if="googleLoading" class="spinner-border spinner-border-sm" />
                  <i v-else class="bi bi-x-circle"></i>
                  {{ googleLoading ? '해제 중...' : '연동 해제' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ✅ 저장 성공 토스트 (disconnect 성공에도 재사용 가능) -->
        <div
          v-if="saved"
          class="toast align-items-center text-bg-success show position-fixed bottom-0 end-0 m-4"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          <div class="d-flex">
            <div class="toast-body">완료되었습니다.</div>
            <button
              type="button"
              class="btn-close btn-close-white me-2 m-auto"
              @click="saved = false"
            ></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import SettingNavBar from '@/components/layout/SettingNavBar.vue'
import axios from 'axios'
import { ensureCsrf, getCookie } from '@/utils/csrf_cors'
import client from '@/api/client'

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'
const googleLogoSrc = '/icons/web_neutral_rd_na@3x.png'

/** 공통 타입 */
type OAuthConnection = {
  connected: boolean
  username?: string
  email?: string
}

/** ✅ 상태 타입: 연동 중 / 연동 안 됨 / 확인 불가 / 연동됨 */
type LinkStatus = 'loading' | 'connected' | 'disconnected' | 'unknown'

const saved = ref(false)

/** ✅ CSRF 포함 공통 요청 헬퍼 */
async function api<T>(
  method: 'get' | 'post' | 'put' | 'patch' | 'delete',
  url: string,
  data?: any,
) {
  await ensureCsrf()
  const csrftoken = getCookie('csrftoken')

  return client.request<T>({
    method,
    url: `${API_BASE}${url}`,
    data,
    withCredentials: true,
    headers: csrftoken ? { 'X-CSRFToken': csrftoken,  } : undefined,
  })
}

/* =========================
 * Discord (로그인 연동만)
 * ========================= */
const discordLoading = ref(false)
const discordConnection = ref<OAuthConnection | null>(null)
const discordStatus = ref<LinkStatus>('loading')

const isDiscordConnected = computed(() => discordStatus.value === 'connected')

const discordStatusLabel = computed(() => {
  switch (discordStatus.value) {
    case 'loading':
      return '연동 중'
    case 'connected':
      return '연동됨'
    case 'disconnected':
      return '연동 안 됨'
    case 'unknown':
    default:
      return '확인 불가'
  }
})

const discordStatusBadgeClass = computed(() => ({
  'text-bg-light text-dark': discordStatus.value === 'loading',
  'text-bg-success': discordStatus.value === 'connected',
  'text-bg-secondary': discordStatus.value === 'disconnected',
  'text-bg-warning': discordStatus.value === 'unknown',
}))

async function fetchDiscordConnection() {
  discordStatus.value = 'loading'
  try {
    const res = await api<OAuthConnection>('get', '/api/discord/connection/')
    discordConnection.value = res.data
    discordStatus.value = res.data.connected ? 'connected' : 'disconnected'
  } catch (e) {
    console.error(e)
    discordStatus.value = 'unknown'
  }
}

async function startDiscordConnect() {
  discordLoading.value = true
  try {
    const res = await api<{ auth_url: string }>('get', '/api/connect_discord/')
    window.location.href = res.data.auth_url
    console.log(res)
  } catch (e) {
    console.error(e)
    discordStatus.value = 'unknown'
  } finally {
    discordLoading.value = false
  }
}

async function disconnectDiscord() {
  discordLoading.value = true
  saved.value = false
  try {
    await api('post', '/api/discord/disconnect/')
    discordConnection.value = { connected: false }
    discordStatus.value = 'disconnected'
    saved.value = true
  } catch (e) {
    console.error(e)
    discordStatus.value = 'unknown'
  } finally {
    discordLoading.value = false
  }
}

/* =========================
 * Google (유지)
 * ========================= */
const googleLoading = ref(false)
const googleConnection = ref<OAuthConnection | null>(null)
const googleStatus = ref<LinkStatus>('loading')

const isGoogleConnected = computed(() => googleStatus.value === 'connected')

const googleStatusLabel = computed(() => {
  switch (googleStatus.value) {
    case 'loading':
      return '연동 중'
    case 'connected':
      return '연동됨'
    case 'disconnected':
      return '연동 안 됨'
    case 'unknown':
    default:
      return '확인 불가'
  }
})

const googleStatusBadgeClass = computed(() => ({
  'text-bg-light text-dark': googleStatus.value === 'loading',
  'text-bg-success': googleStatus.value === 'connected',
  'text-bg-secondary': googleStatus.value === 'disconnected',
  'text-bg-warning': googleStatus.value === 'unknown',
}))

async function fetchGoogleConnection() {
  googleStatus.value = 'loading'
  try {
    const res = await api<OAuthConnection>('get', '/api/google/connection/')
    googleConnection.value = res.data
    googleStatus.value = res.data.connected ? 'connected' : 'disconnected'
  } catch (e) {
    console.error(e)
    googleStatus.value = 'unknown'
  }
}

async function startGoogleConnect() {
  googleLoading.value = true
  try {
    const res = await api<{ auth_url: string }>('get', '/api/google/authorize-url/')
    window.location.href = res.data.auth_url
  } catch (e) {
    console.error(e)
    googleStatus.value = 'unknown'
  } finally {
    googleLoading.value = false
  }
}

async function disconnectGoogle() {
  googleLoading.value = true
  saved.value = false
  try {
    await api('post', '/api/google/disconnect/')
    googleConnection.value = { connected: false }
    googleStatus.value = 'disconnected'
    saved.value = true
  } catch (e) {
    console.error(e)
    googleStatus.value = 'unknown'
  } finally {
    googleLoading.value = false
  }
}

onMounted(() => {
  fetchDiscordConnection()
  fetchGoogleConnection()
})
</script>

<style scoped>
/* =========================
 * Discord: 브랜드 버튼
 * ========================= */
.discord-btn {
  background-color: #5865f2;
  color: #fff;
  border: 1px solid #5865f2;
}

.discord-btn:hover {
  background-color: #4752c4;
  border-color: #4752c4;
  color: #fff;
}

.discord-btn:disabled {
  background-color: #5865f2;
  border-color: #5865f2;
  opacity: 0.65;
}

/* =========================
 * Google: 정책 친화(흰바탕+회색 테두리)
 * ========================= */
.google-btn {
  background-color: #fff;
  color: #3c4043;
  border: 1px solid #dadce0;
  font-weight: 500;
}

.google-btn:hover {
  background-color: #f7f8f8;
  color: #3c4043;
  border-color: #dadce0;
}

.google-btn:disabled {
  background-color: #fff;
  border-color: #dadce0;
  opacity: 0.6;
}
</style>
