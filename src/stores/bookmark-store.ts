import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type Bookmark, type BookmarkData } from '../services/api'

export const useBookmarkStore = defineStore('bookmark', () => {
  const bookmarks = ref<Bookmark[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const bookmarkedIds = ref<Set<string>>(new Set())

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (value: string | null) => {
    error.value = value
  }

  const addBookmark = async (data: BookmarkData) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.addBookmark(data)
      bookmarks.value.unshift(result)
      bookmarkedIds.value.add(data.paper_id)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const removeBookmark = async (paperId: string) => {
    try {
      setLoading(true)
      setError(null)
      await apiService.removeBookmark(paperId)
      bookmarks.value = bookmarks.value.filter(b => b.paper_id !== paperId)
      bookmarkedIds.value.delete(paperId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const toggleBookmark = async (data: BookmarkData) => {
    if (bookmarkedIds.value.has(data.paper_id)) {
      await removeBookmark(data.paper_id)
      return false
    } else {
      await addBookmark(data)
      return true
    }
  }

  const checkBookmark = async (paperId: string) => {
    try {
      const result = await apiService.checkBookmark(paperId)
      if (result.is_bookmarked) {
        bookmarkedIds.value.add(paperId)
      } else {
        bookmarkedIds.value.delete(paperId)
      }
      return result.is_bookmarked
    } catch (err) {
      console.error('Error checking bookmark:', err)
      return false
    }
  }

  const isBookmarked = (paperId: string) => {
    return bookmarkedIds.value.has(paperId)
  }

  const fetchBookmarks = async (limit: number = 100, offset: number = 0) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.getBookmarks(limit, offset)
      bookmarks.value = result.items
      result.items.forEach(item => bookmarkedIds.value.add(item.paper_id))
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const searchBookmarks = async (query: string, limit: number = 10) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiService.searchBookmarks(query, limit)
      bookmarks.value = result.items
      return result.items
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    bookmarks,
    loading,
    error,
    bookmarkedIds,
    addBookmark,
    removeBookmark,
    toggleBookmark,
    checkBookmark,
    isBookmarked,
    fetchBookmarks,
    searchBookmarks,
    setLoading,
    setError,
  }
})
