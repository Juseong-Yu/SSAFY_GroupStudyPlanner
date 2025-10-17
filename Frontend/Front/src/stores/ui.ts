import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isLgUp = ref(window.innerWidth >= 992)
  const sidebarOpen = ref(isLgUp.value) // lg 이상 기본 오픈

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
    if (isLgUp.value) openSidebar()
    else closeSidebar()
  }

  return { isLgUp, sidebarOpen, toggleSidebar, openSidebar, closeSidebar, handleResize }
})
