import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FollowedAuthor } from '@/types/followedAuthor'
import { followedAuthorApi } from '@/services/followedAuthor'

export const useFollowedAuthorStore = defineStore('followedAuthor', () => {
  const followedAuthors = ref<FollowedAuthor[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const followedCache = ref<Map<string, boolean>>(new Map())

  const sortedAuthors = computed(() => {
    return [...followedAuthors.value].sort(
      (a, b) => new Date(b.followed_at).getTime() - new Date(a.followed_at).getTime()
    )
  })

  async function fetchFollowedAuthors(limit: number = 2000, offset: number = 0) {
    loading.value = true
    error.value = null
    try {
      const response = await followedAuthorApi.getFollowedAuthors(limit, offset)
      followedAuthors.value = response.items
      total.value = response.total
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch followed authors'
    } finally {
      loading.value = false
    }
  }

  async function followAuthor(authorName: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const author = await followedAuthorApi.followAuthor(authorName)
      followedAuthors.value.unshift(author)
      total.value += 1
      followedCache.value.set(authorName, true)
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to follow author'
      return false
    } finally {
      loading.value = false
    }
  }

  async function unfollowAuthor(authorName: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await followedAuthorApi.unfollowAuthor(authorName)
      followedAuthors.value = followedAuthors.value.filter((a) => a.author_name !== authorName)
      total.value -= 1
      followedCache.value.set(authorName, false)
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to unfollow author'
      return false
    } finally {
      loading.value = false
    }
  }

  async function checkIfFollowed(authorName: string): Promise<boolean> {
    if (followedCache.value.has(authorName)) {
      return followedCache.value.get(authorName) || false
    }

    try {
      const response = await followedAuthorApi.isFollowed(authorName)
      followedCache.value.set(authorName, response.is_followed)
      return response.is_followed
    } catch {
      return false
    }
  }

  async function updateNotes(authorName: string, notes: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const updated = await followedAuthorApi.updateNotes(authorName, notes)
      const index = followedAuthors.value.findIndex((a) => a.author_name === authorName)
      if (index !== -1) {
        followedAuthors.value[index] = updated
      }
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to update notes'
      return false
    } finally {
      loading.value = false
    }
  }

  function clearCache() {
    followedCache.value.clear()
  }

  return {
    followedAuthors,
    total,
    loading,
    error,
    sortedAuthors,
    fetchFollowedAuthors,
    followAuthor,
    unfollowAuthor,
    checkIfFollowed,
    updateNotes,
    clearCache,
  }
})
