import { computed } from 'vue'
import { useConfigStore } from '@/stores/config-store'
import { CATEGORY_GROUPS } from '@/utils/categoryColors'

export interface SubjectOption {
  id: string
  name: string
  color: string
  icon: string
}

export function useSubjectSwitch() {
  const configStore = useConfigStore()

  // Subject options with colors and icons
  const subjectOptions: SubjectOption[] = CATEGORY_GROUPS.map(group => ({
    id: group.id,
    name: group.name,
    color: group.color,
    icon: group.icon
  }))

  // Current subject
  const currentSubject = computed(() => configStore.defaultSubject)

  // Get current subject info
  const currentSubjectInfo = computed(() => {
    return subjectOptions.find(s => s.id === currentSubject.value) || subjectOptions[0]
  })

  // Set default subject and reload page
  const setDefaultSubject = (subject: string) => {
    const currentSubjectValue = configStore.defaultSubject
    if (currentSubjectValue !== subject) {
      configStore.setDefaultSubject(subject)
      // Refresh page to ensure all components reinitialize with new subject
      window.location.reload()
    }
  }

  return {
    subjectOptions,
    currentSubject,
    currentSubjectInfo,
    setDefaultSubject
  }
}