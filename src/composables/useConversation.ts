import { ref } from 'vue'
import { useConversationStore, type ChatMode } from '../stores/conversation-store'

export function useConversation() {
  const conversationStore = useConversationStore()
  
  const searchQuery = ref('')
  const editingId = ref<string | null>(null)
  const showDeleteConfirm = ref(false)
  const deleteTargetId = ref<string | null>(null)
  
  function formatDate(dateStr: string) {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' })
  }
  
  let searchTimeout: ReturnType<typeof setTimeout> | null = null
  function handleSearch() {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(async () => {
      if (searchQuery.value.trim()) {
        await conversationStore.searchConversations(searchQuery.value)
      } else {
        await conversationStore.loadConversations()
      }
    }, 300)
  }
  
  function startEdit(sessionId: string) {
    editingId.value = sessionId
  }
  
  async function updateTitle(sessionId: string, event: FocusEvent) {
    const target = event.target as HTMLElement
    const newTitle = target.textContent?.trim() || 'Untitled'
    await conversationStore.updateConversation(sessionId, { title: newTitle })
    editingId.value = null
  }
  
  async function toggleStar(sessionId: string) {
    const conversation = conversationStore.conversations.find(c => c.session_id === sessionId)
    if (conversation) {
      await conversationStore.updateConversation(sessionId, { starred: !conversation.starred })
    }
  }
  
  async function togglePin(sessionId: string) {
    const conversation = conversationStore.conversations.find(c => c.session_id === sessionId)
    if (conversation) {
      await conversationStore.updateConversation(sessionId, { pinned: !conversation.pinned })
    }
  }
  
  function confirmDelete(sessionId: string) {
    deleteTargetId.value = sessionId
    showDeleteConfirm.value = true
  }
  
  async function executeDelete() {
    if (deleteTargetId.value) {
      await conversationStore.deleteConversation(deleteTargetId.value)
      showDeleteConfirm.value = false
      deleteTargetId.value = null
    }
  }
  
  function cancelDelete() {
    showDeleteConfirm.value = false
    deleteTargetId.value = null
  }
  
  return {
    searchQuery,
    editingId,
    showDeleteConfirm,
    deleteTargetId,
    
    formatDate,
    handleSearch,
    startEdit,
    updateTitle,
    toggleStar,
    togglePin,
    confirmDelete,
    executeDelete,
    cancelDelete,
  }
}

export type { ChatMode }
