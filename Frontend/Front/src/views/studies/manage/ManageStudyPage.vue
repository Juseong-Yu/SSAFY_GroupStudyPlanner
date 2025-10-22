<!-- src/views/MainPage.vue -->
<template>
  <AppShell>
    <div class="d-flex flex-column justify-content-center align-items-center min-vh-100">
      <!-- ✅ 달력 -->
      <div v-if="isMounted" class="calendar-wrapper w-100 px-3" style="max-width: 1000px">
        <FullCalendar :options="calendarOptions" class="w-100" />
      </div>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { ref, onMounted } from 'vue'

// ✅ FullCalendar v6 (자동 CSS 주입됨)
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'

const isMounted = ref(false)

onMounted(() => {
  isMounted.value = true
})

// ✅ 옵션 기반 설정 (v6 권장 방식)
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  height: 'auto',
  locale: 'ko', // 한국어로 표시 (요일 등)
  selectable: true,
  events: [
    { title: '스터디 회의', start: '2025-10-24' },
    { title: '알고리즘 과제 마감', start: '2025-10-27' },
  ],
  dateClick: (info: any) => {
    alert(`선택한 날짜: ${info.dateStr}`)
  },
})
</script>

<style scoped>
.main-logo {
  max-width: 300px;
  height: auto;
}

/* ✅ 달력 기본 스타일만 살짝 */
.calendar-wrapper :deep(.fc) {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1rem;
}

:deep(.fc-toolbar-title) {
  color: #2b3a67;
  font-weight: 700;
}

:deep(.fc-col-header-cell) {
  background-color: #f7f9fc;
  font-weight: 600;
  color: #3b4b70;
}

/* ✅ 날짜 숫자(앵커)에서 '링크 느낌' 제거 */
:deep(.fc .fc-daygrid-day-number),
:deep(.fc .fc-daygrid-day-number:link),
:deep(.fc .fc-daygrid-day-number:visited),
:deep(.fc .fc-daygrid-day-number:hover),
:deep(.fc .fc-daygrid-day-number:focus),
:deep(.fc .fc-daygrid-day-number:active) {
  color: inherit !important; /* 파란 링크색 제거 */
  text-decoration: none !important; /* 밑줄 제거 */
  cursor: default !important; /* 손가락 커서 제거 */
  outline: none !important; /* 포커스 아웃라인 제거 */
}

/* ✅ 날짜 셀에 은은한 hover만 (선택사항) */
:deep(.fc .fc-daygrid-day:hover) {
  background-color: #fafcff; /* 가벼운 하이라이트 */
}

/* ✅ 이벤트 텍스트도 링크 표시 감추기(앵커 밑줄 등) */
:deep(.fc .fc-daygrid-event a) {
  color: inherit;
  text-decoration: none;
}
:deep(.fc .fc-daygrid-event:hover) {
  filter: brightness(0.98);
}
</style>
