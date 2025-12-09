import { useUserStore } from './user'
import { useUiStore } from './ui'
import { useStudiesStore } from './studies'
import { useStudyRoleStore } from './studyRoleStore'

export function resetAllStores() {
  useUserStore().reset()
  useUiStore().reset()
  useStudiesStore().reset()
  useStudyRoleStore().resetAll()
}
