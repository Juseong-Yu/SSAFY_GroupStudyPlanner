import { watch, onBeforeUnmount, type Ref } from 'vue'

type Options = {
  closeOnEsc?: boolean
  closeOnOutside?: boolean
}

export function useModalAutoClose(
  isOpen: Ref<boolean>,
  modalRootRef: Ref<HTMLElement | null>,
  close: () => void,
  options: Options = {},
) {
  const { closeOnEsc = true, closeOnOutside = true } = options

  const onPointerDownCapture = (e: PointerEvent) => {
    if (!isOpen.value) return
    if (!closeOnOutside) return

    const root = modalRootRef.value
    if (!root) return

    const target = e.target as Node | null
    // ✅ modalRoot 바깥 클릭이면 닫기
    if (target && !root.contains(target)) close()
  }

  const onKeydown = (e: KeyboardEvent) => {
    if (!isOpen.value) return
    if (!closeOnEsc) return
    if (e.key === 'Escape') close()
  }

  const bind = () => {
    document.addEventListener('pointerdown', onPointerDownCapture, true) // capture
    document.addEventListener('keydown', onKeydown)
  }

  const unbind = () => {
    document.removeEventListener('pointerdown', onPointerDownCapture, true)
    document.removeEventListener('keydown', onKeydown)
  }

  // ✅ 열릴 때만 리스너 붙이고 닫히면 제거
  watch(
    isOpen,
    (open) => {
      if (open) bind()
      else unbind()
    },
    { immediate: true },
  )

  onBeforeUnmount(() => {
    unbind()
  })
}
