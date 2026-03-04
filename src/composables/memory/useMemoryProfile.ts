import { ref, computed } from 'vue'
import { useMemoryStore } from '@/stores/memory-store'
import { useToastStore } from '@/stores/toast-store'

export function useMemoryProfile() {
  const memoryStore = useMemoryStore()
  const toastStore = useToastStore()
  
  const newInterest = ref('')
  const newDomain = ref('')
  const isSaving = ref(false)
  
  const profile = computed(() => memoryStore.coreMemory)
  
  const addInterest = async () => {
    if (!newInterest.value.trim()) return
    const current = memoryStore.coreMemory?.research_interests || []
    if (current.includes(newInterest.value.trim())) {
      newInterest.value = ''
      return
    }
    await memoryStore.updateCoreMemory({
      research_interests: [...current, newInterest.value.trim()],
    })
    newInterest.value = ''
  }
  
  const removeInterest = async (interest: string) => {
    const current = memoryStore.coreMemory?.research_interests || []
    await memoryStore.updateCoreMemory({
      research_interests: current.filter(i => i !== interest),
    })
  }
  
  const addDomain = async () => {
    if (!newDomain.value.trim()) return
    const current = memoryStore.coreMemory?.preferred_domains || []
    if (current.includes(newDomain.value.trim())) {
      newDomain.value = ''
      return
    }
    await memoryStore.updateCoreMemory({
      preferred_domains: [...current, newDomain.value.trim()],
    })
    newDomain.value = ''
  }
  
  const removeDomain = async (domain: string) => {
    const current = memoryStore.coreMemory?.preferred_domains || []
    await memoryStore.updateCoreMemory({
      preferred_domains: current.filter(d => d !== domain),
    })
  }
  
  const setLanguagePreference = async (preference: string) => {
    await memoryStore.updateCoreMemory({ language_preference: preference })
  }
  
  const setSummaryStyle = async (style: 'detailed' | 'brief' | 'bullet_points') => {
    await memoryStore.updateCoreMemory({ summary_style: style })
  }
  
  const updateCustomInstructions = async (instructions: string) => {
    await memoryStore.updateCoreMemory({ custom_instructions: instructions })
  }
  
  const handleSave = async () => {
    const p = profile.value
    if (!p) return
    
    isSaving.value = true
    try {
      await memoryStore.updateCoreMemory({
        research_interests: p.research_interests,
        preferred_domains: p.preferred_domains,
        frequently_used_skills: p.frequently_used_skills,
        language_preference: p.language_preference,
        summary_style: p.summary_style,
        custom_instructions: p.custom_instructions,
      })
      toastStore.showSuccess('Profile saved successfully')
    } catch {
      toastStore.showError('Failed to save profile')
    } finally {
      isSaving.value = false
    }
  }
  
  return {
    profile,
    newInterest,
    newDomain,
    isSaving,
    addInterest,
    removeInterest,
    addDomain,
    removeDomain,
    setLanguagePreference,
    setSummaryStyle,
    updateCustomInstructions,
    handleSave,
  }
}
