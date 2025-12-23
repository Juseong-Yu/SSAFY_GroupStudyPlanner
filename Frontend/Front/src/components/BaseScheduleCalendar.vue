<!-- src/components/calendar/BaseScheduleCalendar.vue -->
<template>
  <div class="card shadow-sm">
    <div
      class="card-body p-3"
      :style="{
        height: resolvedHeight,
        display: 'flex',
        flexDirection: 'column',
      }"
    >
      <div v-if="loading && !isMounted" class="py-5 text-center text-muted small">
        불러오는 중...
      </div>

      <div v-else-if="isMounted" class="calendar-wrapper" style="flex: 1">
        <FullCalendar ref="calendarRef" :options="calendarOptions" />
      </div>
    </div>
  </div>

  <slot name="footer" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { CalendarOptions, EventInput, DatesSetArg, EventClickArg } from '@fullcalendar/core'

const props = defineProps<{
  events: EventInput[]
  loading?: boolean
  height?: string
}>()

const emit = defineEmits<{
  (e: 'event-click', payload: EventClickArg): void
  (e: 'dates-change', payload: DatesSetArg): void
}>()

const isMounted = ref(false)
const calendarRef = ref<InstanceType<typeof FullCalendar> | null>(null)

const resolvedHeight = computed(() => props.height || 'calc(100vh - 220px)')

const calendarOptions = computed<CalendarOptions>(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  height: '100%',
  expandRows: true,
  locale: 'ko',
  selectable: true,
  timeZone: 'KST',

  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek', // ✅ 월 / 주 둘 다 dayGrid 계열
  },
  buttonText: {
    today: '오늘',
    month: '월간',
    week: '주간',
  },

  // ✅ 월간 / 주간 둘 다 "시간 텍스트" 완전 숨김
  views: {
    dayGridMonth: {
      displayEventTime: false,
    },
    dayGridWeek: {
      displayEventTime: false,
    },
  },

  // ✅ 날짜 클릭 → 해당 날짜가 포함된 주간(dayGridWeek)으로 전환
  dateClick: (info: any) => {
    const api = calendarRef.value?.getApi()
    if (api) {
      api.changeView('dayGridWeek', info.date)
    }
  },

  events: props.events,

  eventClick: (info: EventClickArg) => {
    emit('event-click', info)
  },

  datesSet: (arg: DatesSetArg) => {
    emit('dates-change', arg)
  },
}))

const getApi = () => calendarRef.value?.getApi()

defineExpose({
  getApi,
  updateSize: () => calendarRef.value?.getApi().updateSize(),
})

onMounted(() => {
  isMounted.value = true
})
</script>

<style scoped>
.calendar-wrapper {
  overflow: auto;
}

.calendar-wrapper :deep(.fc) {
  height: 100%;
  background-color: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0.5rem;
}

/* FullCalendar 스타일 */
:deep(.fc-toolbar-title) {
  color: #2b3a67;
  font-weight: 700;
}

:deep(.fc .fc-daygrid-day-number) {
  color: #212529;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-day-number:hover),
:deep(.fc .fc-daygrid-day-number:focus) {
  color: #212529;
}

:deep(.fc a) {
  color: inherit;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-event) {
  color: #212529;
}

:deep(.fc .fc-col-header-cell-cushion) {
  color: #3b4b70;
  text-decoration: none;
}

:deep(.fc .fc-daygrid-day:hover) {
  background: #fafcff;
}

/* 캘린더 스크롤 */
:deep(.fc .fc-scroller) {
  overflow: auto !important;
  max-height: 100%;
}

/* 툴바 버튼 커스텀 (텍스트 탭 느낌) */
:deep(.fc .fc-toolbar.fc-header-toolbar) {
  margin-bottom: 0.75rem;
}

:deep(.fc .fc-button) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #64748b !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  padding: 0.25rem 0.4rem !important;
  border-radius: 999px !important;
  text-transform: none !important;
}

:deep(.fc .fc-button:hover) {
  background: rgba(148, 163, 184, 0.12) !important;
  color: #475569 !important;
}

:deep(.fc .fc-button-group .fc-button.fc-button-active) {
  background: transparent !important;
  color: #1e293b !important;
  position: relative;
}

:deep(.fc .fc-button-group .fc-button.fc-button-active::after) {
  content: '';
  position: absolute;
  left: 0.4rem;
  right: 0.4rem;
  bottom: -0.15rem;
  height: 2px;
  border-radius: 999px;
  background: #60a5fa;
}

:deep(.fc .fc-prev-button),
:deep(.fc .fc-next-button) {
  border-radius: 999px !important;
  background: transparent !important;
  border: none !important;
  padding: 0.15rem 0.45rem !important;
}

:deep(.fc .fc-prev-button:hover),
:deep(.fc .fc-next-button:hover) {
  background: rgba(148, 163, 184, 0.12) !important;
}

:deep(.fc .fc-today-button) {
  border-radius: 999px !important;
  padding: 0.2rem 0.6rem !important;
  border: 1px solid #d0e2ff !important;
  background: #eff6ff !important;
  color: #1d4ed8 !important;
}

:deep(.fc .fc-today-button:disabled) {
  opacity: 0.6;
  background: #f3f4f6 !important;
  border-color: #e5e7eb !important;
  color: #9ca3af !important;
}

/* 월간/주간 공통: 이벤트 사이 간격 확보 */
:deep(.fc-daygrid-event) {
  margin-top: 2px !important;
  margin-bottom: 4px !important;
}

/* 월간: 너무 두껍지 않게 */
:deep(.fc-dayGridMonth-view .fc-daygrid-event) {
  min-height: 20px;
}

/* 주간: 더 두껍게 */
:deep(.fc-dayGridWeek-view .fc-daygrid-event) {
  min-height: 40px;
}
</style>
