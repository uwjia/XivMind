import { ref } from 'vue'
import type { Message } from './useChatMessages'

export function useMessageCopy() {
  const copiedMessageId = ref<string | null>(null)

  const getMessageId = (message: Message): string => {
    return `${message.role}-${message.content.substring(0, 50)}-${message.papers?.length || 0}-${message.answer?.substring(0, 50) || ''}`
  }

  const formatMessageForCopy = (message: Message): string => {
    if (message.answer) {
      let text = message.answer
      if (message.references && message.references.length > 0) {
        text += '\n\nReferences:\n'
        message.references.forEach((ref, index) => {
          text += `${index + 1}. ${ref.title} - ${ref.authors?.join(', ')}\n`
        })
      }
      return text
    }
    
    if (message.papers && message.papers.length > 0) {
      let text = `Found ${message.papers.length} papers:\n\n`
      message.papers.forEach((paper, index) => {
        text += `${index + 1}. ${paper.title}\n`
        text += `   Authors: ${paper.authors?.join(', ')}\n`
        text += `   Category: ${paper.primary_category}\n`
        text += `   Published: ${paper.published}\n`
        text += `   Similarity: ${(paper.similarity_score * 100).toFixed(1)}%\n\n`
      })
      return text
    }
    
    return message.content
  }

  const copyMessage = async (message: Message): Promise<boolean> => {
    const textToCopy = formatMessageForCopy(message)
    
    try {
      await navigator.clipboard.writeText(textToCopy)
      const msgId = getMessageId(message)
      copiedMessageId.value = msgId
      setTimeout(() => {
        if (copiedMessageId.value === msgId) {
          copiedMessageId.value = null
        }
      }, 2000)
      return true
    } catch (err) {
      console.error('Failed to copy:', err)
      return false
    }
  }

  const isCopied = (message: Message): boolean => {
    return copiedMessageId.value === getMessageId(message)
  }

  return {
    copiedMessageId,
    getMessageId,
    formatMessageForCopy,
    copyMessage,
    isCopied
  }
}
