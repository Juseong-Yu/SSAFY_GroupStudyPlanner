import { useUserStore } from './user'
import { useUiStore } from './ui'
import { useStudiesStore } from './studies'

export function resetAllStores() {
  useUserStore().reset()
  useUiStore().reset()
  useStudiesStore().reset()
}
