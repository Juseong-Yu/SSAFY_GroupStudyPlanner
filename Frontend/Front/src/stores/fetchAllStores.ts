import { useUserStore } from './user'
import { useStudiesStore } from './studies'
import { useUiStore } from './ui'

export async function fetchAllStores() {
  const user = useUserStore()
  const studies = useStudiesStore()
  const ui = useUiStore()

  // 유저 정보 로드
  await user.loadIfNeeded({ force: true })

  // 스터디 목록 로드
  await studies.loadIfNeeded({ force: true })

  // UI는 보통 fetch가 없으므로 필요시만
  ui.reset() // or skip
}
