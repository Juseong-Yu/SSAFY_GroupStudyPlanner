import { defineStore } from 'pinia'
import { ref } from 'vue'

// 초기 상태 생성 함수
function initialState() {
  const isLgUp = window.innerWidth >= 992
  return {
    isLgUp,
    sidebarOpen: isLgUp,
  }
}

export const useUiStore = defineStore('ui', () => {
  // 초기 상태 적용
  const state = initialState()

  const isLgUp = ref(state.isLgUp)
  const sidebarOpen = ref(state.sidebarOpen)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function openSidebar() {
    sidebarOpen.value = true
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function handleResize() {
    isLgUp.value = window.innerWidth >= 992
  }

  // reset 함수 추가
  function reset() {
    const s = initialState()
    isLgUp.value = s.isLgUp
    sidebarOpen.value = s.sidebarOpen
  }

  return {
    isLgUp,
    sidebarOpen,
    toggleSidebar,
    openSidebar,
    closeSidebar,
    handleResize,
    reset, // ⬅ 여기에 포함!
  }
})
