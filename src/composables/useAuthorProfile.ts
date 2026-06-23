import { ref, computed } from 'vue'
import { API_BASE_URL } from '@/services/config'
import { useConfigStore } from '@/stores/config-store'
import type { AuthorProfile } from '@/types/author'

const BACKEND_API_BASE = `${API_BASE_URL}/api/arxiv`

export function useAuthorProfile() {
  const configStore = useConfigStore()
  const profile = ref<AuthorProfile | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasData = computed(() => profile.value && profile.value.total_papers > 0)

  async function fetchProfile(authorName: string) {
    loading.value = true
    error.value = null
    profile.value = null

    try {
      const encodedName = encodeURIComponent(authorName)
      const params = new URLSearchParams({
        subject: configStore.defaultSubject
      })
      const response = await fetch(`${BACKEND_API_BASE}/author/${encodedName}/profile?${params}`)

      if (!response.ok) {
        throw new Error(`Failed to fetch author profile: ${response.statusText}`)
      }

      const data = await response.json()
      profile.value = data as AuthorProfile

      if (data.error) {
        error.value = data.error
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch author profile'
      profile.value = null
    } finally {
      loading.value = false
    }
  }

  function reset() {
    profile.value = null
    loading.value = false
    error.value = null
  }

  return {
    profile,
    loading,
    error,
    hasData,
    fetchProfile,
    reset,
  }
}
