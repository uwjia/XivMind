<template>
  <div class="assistant-page">
    <div class="page-header">
      <h1>AI Assistant</h1>
      <p class="subtitle">Search papers or ask questions about research topics</p>
      <div class="header-controls">
        <div class="mode-switch">
          <button 
            :class="['mode-btn', { active: mode === 'search' }]" 
            @click="mode = 'search'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <span>Search</span>
          </button>
          <button 
            :class="['mode-btn', { active: mode === 'ask' }]" 
            @click="mode = 'ask'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span>Ask</span>
          </button>
          <button 
            :class="['mode-btn', { active: mode === 'skills' }]" 
            @click="mode = 'skills'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
            <span>Skills</span>
          </button>
        </div>
      </div>
    </div>

    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg v-if="mode === 'search'" viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"/>
            </svg>
          </div>
          <h3>{{ mode === 'search' ? 'Search Papers' : mode === 'ask' ? 'Ask Questions' : 'Select a Skill' }}</h3>
          <p v-if="mode === 'search'">Enter a natural language query to find relevant papers using semantic search.</p>
          <p v-else-if="mode === 'ask'">Ask questions about research topics and get AI-powered answers with paper references.</p>
          <p v-else>Select a skill to perform specific tasks on papers.</p>
          
          <div v-if="mode === 'skills'" class="skills-panel">
            <div v-if="skillsLoading" class="skills-loading">
              <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="24" height="24">
                <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
              </svg>
              <span>Loading skills...</span>
            </div>
            <div v-else class="skills-grid">
              <div 
                v-for="skill in skills" 
                :key="skill.id" 
                class="skill-card"
                :class="{ disabled: !skill.available, dynamic: skill.source === 'dynamic' }"
                @click="selectSkill(skill)"
              >
                <div class="skill-icon">
                  <svg v-if="skill.icon === 'file-text'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                  <svg v-else-if="skill.icon === 'languages'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" y1="12" x2="22" y2="12"/>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                  <svg v-else-if="skill.icon === 'quote'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/>
                    <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/>
                  </svg>
                  <svg v-else-if="skill.icon === 'link'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 16v-4"/>
                    <path d="M12 8h.01"/>
                  </svg>
                </div>
                <div class="skill-info">
                  <div class="skill-name">{{ skill.name }}</div>
                  <div class="skill-desc">{{ skill.description }}</div>
                </div>
                <div class="skill-meta">
                  <span class="skill-category">{{ skill.category }}</span>
                  <span 
                    v-if="skill.source === 'dynamic'" 
                    class="skill-source dynamic"
                  >
                    Dynamic
                  </span>
                  <span 
                    v-else 
                    class="skill-source builtin"
                  >
                    Built-in
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="suggestions">
            <button v-for="suggestion in currentSuggestions" :key="suggestion" class="suggestion-btn" @click="sendSuggestion(suggestion)">
              {{ suggestion }}
            </button>
          </div>
        </div>

        <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role" :ref="el => setMessageRef(el, index)">
          <div class="message-avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <div class="message-content">
            <div v-if="message.papers && message.papers.length > 0" class="papers-result">
              <div class="result-header">
                Found {{ message.papers.length }} papers
                <span v-if="message.model" class="model-badge">{{ message.model }}</span>
              </div>
              <div class="paper-cards">
                <div v-for="paper in message.papers" :key="paper.id" class="paper-card" @click="$emit('viewPaper', paper.id)">
                  <div class="paper-header">
                    <h4 class="paper-title">{{ paper.title }}</h4>
                    <span class="similarity-score">{{ (paper.similarity_score * 100).toFixed(1) }}%</span>
                  </div>
                  <p class="paper-authors">{{ paper.authors?.slice(0, 3).join(', ') }}{{ paper.authors?.length > 3 ? ' et al.' : '' }}</p>
                  <p class="paper-abstract">{{ paper.abstract?.substring(0, 200) }}{{ paper.abstract?.length > 200 ? '...' : '' }}</p>
                  <div class="paper-meta">
                    <span class="paper-category">{{ paper.primary_category }}</span>
                    <span class="paper-date">{{ paper.published?.substring(0, 10) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="message.answer" class="answer-result">
              <div class="answer-text" v-html="formatMessage(message.answer)"></div>
              <div v-if="message.references && message.references.length > 0" class="references">
                <h5>📚 References</h5>
                <div v-for="ref in message.references" :key="ref.id" class="reference-item" @click="$emit('viewPaper', ref.id)">
                  <span class="ref-title">{{ ref.title }}</span>
                  <span class="ref-authors">{{ ref.authors?.slice(0, 2).join(', ') }}</span>
                  <span class="ref-score">{{ (ref.relevance_score * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
            <div v-else class="message-text" v-html="formatMessage(message.content)"></div>
            <div v-if="message.isConfigError" class="config-error-hint">
              <button @click="goToSettings" class="settings-link-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
                Go to Settings to configure LLM Provider
              </button>
            </div>
            <div v-if="message.role === 'assistant'" class="message-actions">
              <button 
                @click="copyMessage(message)" 
                class="action-icon-btn"
                :title="copiedMessageId === getMessageId(message) ? 'Copied!' : 'Copy all'"
              >
                <svg v-if="copiedMessageId === getMessageId(message)" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
              <button 
                v-if="message.answer || message.papers || message.content"
                @click="retryMessage(message)" 
                class="action-icon-btn"
                title="Retry"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M23 4v6h-6"/>
                  <path d="M1 20v-6h6"/>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10B981">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <template v-if="mode === 'skills' && selectedSkill && !skillExecuted">
          <SkillForm
            :skill="selectedSkill"
            @submit="handleSkillExecute"
            @cancel="backToSkills"
          />
        </template>
        <template v-else-if="mode === 'skills' && selectedSkill && skillExecuted">
          <div class="skill-actions-bar">
            <button @click="runSkillAgain" class="action-btn run-again">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              <span>Run Again</span>
            </button>
            <button @click="backToSkills" class="action-btn back-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
              <span>Back to Skills</span>
            </button>
          </div>
        </template>
        <template v-else>
          <textarea
            v-model="inputMessage"
            @keydown.enter.exact.prevent="sendMessage()"
            :placeholder="mode === 'search' ? 'Enter your search query...' : 'Ask a question about research...'"
            rows="1"
            ref="inputRef"
          ></textarea>
          <button @click="sendMessage()" :disabled="!inputMessage.trim() || isLoading" class="send-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { arxivBackendAPI } from '../services/arxivBackend'
import { skillsAPI } from '../services/skills'
import type { Skill, RelatedPaper } from '../services/skills'
import { useLLMStore } from '../stores/llm-store'
import SkillForm from '../components/skills/SkillForm.vue'

interface Paper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  similarity_score: number
}

interface Reference {
  id: string
  title: string
  authors: string[]
  published?: string
  relevance_score: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  papers?: Paper[]
  answer?: string
  references?: Reference[]
  model?: string
  isConfigError?: boolean
  skillId?: string
  skillName?: string
  paperIds?: string[]
  skillParams?: Record<string, unknown>
}

const router = useRouter()
const llmStore = useLLMStore()

const isConfigError = (errorMsg: string): boolean => {
  const configErrorPatterns = [
    /api[_-]?key/i,
    /not configured/i,
    /missing.*key/i,
    /key is required/i,
    /authentication/i,
    /unauthorized/i,
    /invalid.*key/i,
    /no provider/i,
    /provider not available/i,
    /400 bad request/i,
    /401/i,
    /403 forbidden/i,
    /connection refused/i,
    /localhost.*11434/i,
    /ollama/i,
    /ECONNREFUSED/i,
    /network error/i,
    /failed to fetch/i,
    /request failed/i
  ]
  return configErrorPatterns.some(pattern => pattern.test(errorMsg))
}

const mode = ref<'search' | 'ask' | 'skills'>('search')
const searchMessages = ref<Message[]>([])
const askMessages = ref<Message[]>([])
const skillsMessages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

const messages = computed({
  get: () => {
    switch (mode.value) {
      case 'search': return searchMessages.value
      case 'ask': return askMessages.value
      case 'skills': return skillsMessages.value
      default: return searchMessages.value
    }
  },
  set: (value: Message[]) => {
    switch (mode.value) {
      case 'search': searchMessages.value = value; break
      case 'ask': askMessages.value = value; break
      case 'skills': skillsMessages.value = value; break
    }
  }
})

const skills = ref<Skill[]>([])
const skillsLoading = ref(false)
const selectedSkill = ref<Skill | null>(null)
const skillExecuted = ref(false)
const copiedMessageId = ref<string | null>(null)
const messageRefs = ref<Map<number, HTMLElement>>(new Map())
const currentUserMessageIndex = ref<number | null>(null)

const setMessageRef = (el: any, index: number) => {
  if (el) {
    messageRefs.value.set(index, el as HTMLElement)
  }
}

const getMessageId = (message: Message): string => {
  return `${message.role}-${message.content.substring(0, 50)}-${message.papers?.length || 0}-${message.answer?.substring(0, 50) || ''}`
}

const copyMessage = async (message: Message) => {
  let textToCopy = ''
  
  if (message.answer) {
    textToCopy = message.answer
    if (message.references && message.references.length > 0) {
      textToCopy += '\n\nReferences:\n'
      message.references.forEach((ref, index) => {
        textToCopy += `${index + 1}. ${ref.title} - ${ref.authors?.join(', ')}\n`
      })
    }
  } else if (message.papers && message.papers.length > 0) {
    textToCopy = `Found ${message.papers.length} papers:\n\n`
    message.papers.forEach((paper, index) => {
      textToCopy += `${index + 1}. ${paper.title}\n   Authors: ${paper.authors?.join(', ')}\n   Category: ${paper.primary_category}\n   Published: ${paper.published}\n   Similarity: ${(paper.similarity_score * 100).toFixed(1)}%\n\n`
    })
  } else {
    textToCopy = message.content
  }
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    const msgId = getMessageId(message)
    copiedMessageId.value = msgId
    setTimeout(() => {
      if (copiedMessageId.value === msgId) {
        copiedMessageId.value = null
      }
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const retryMessage = async (message: Message) => {
  const messageIndex = messages.value.findIndex(m => getMessageId(m) === getMessageId(message))
  if (messageIndex <= 0) return
  
  const userMessage = messages.value[messageIndex - 1]
  if (userMessage.role !== 'user') return
  
  messages.value = messages.value.slice(0, messageIndex)
  
  if (userMessage.skillId && userMessage.paperIds && userMessage.skillParams) {
    const skill = skills.value.find(s => s.id === userMessage.skillId)
    if (skill) {
      selectedSkill.value = skill
      skillExecuted.value = false
      
      await handleSkillExecute(userMessage.paperIds, userMessage.skillParams)
    }
  } else {
    const originalInput = userMessage.content
    inputMessage.value = originalInput
    
    await sendMessage(true)
  }
}

watch(mode, (newMode) => {
  currentUserMessageIndex.value = null
  if (newMode === 'ask' && llmStore.providers.length === 0) {
    llmStore.init()
  }
  if (newMode === 'skills') {
    selectedSkill.value = null
    skillExecuted.value = false
    if (skills.value.length === 0) {
      loadSkills()
    }
  }
})

const loadSkills = async () => {
  skillsLoading.value = true
  try {
    const result = await skillsAPI.getSkills()
    skills.value = result.skills || []
  } catch (error) {
    console.error('Failed to load skills:', error)
  } finally {
    skillsLoading.value = false
  }
}

const selectSkill = (skill: Skill) => {
  if (!skill.available) return
  selectedSkill.value = skill
  skillExecuted.value = false
  messages.value = []
}

const handleSkillExecute = async (paperIds: string[], params: Record<string, unknown>) => {
  if (!selectedSkill.value) return
  
  skillExecuted.value = true
  
  const paperIdText = paperIds.length > 0 ? paperIds.join(', ') : 'No paper ID'
  messages.value.push({ 
    role: 'user', 
    content: `**${selectedSkill.value.name}** on: ${paperIdText}`,
    skillId: selectedSkill.value.id,
    skillName: selectedSkill.value.name,
    paperIds: paperIds,
    skillParams: params
  })
  
  currentUserMessageIndex.value = messages.value.length - 1
  scrollToBottom()
  isLoading.value = true
  
  try {
    const result = await skillsAPI.executeSkill(
      selectedSkill.value.id,
      paperIds,
      params,
      llmStore.selectedProvider || undefined,
      llmStore.selectedModel || undefined
    )
    
    if (result.success) {
      let responseContent = ''
      
      if (result.summary) {
        responseContent = `**Summary**\n\n${result.summary}`
      } else if (result.translation) {
        responseContent = `**Translation (${result.target_language})**\n\n${result.translation}`
      } else if (result.citations) {
        responseContent = '**Citations**\n\n'
        for (const [format, citation] of Object.entries(result.citations)) {
          responseContent += `**${format}:**\n\`\`\`\n${citation}\n\`\`\`\n\n`
        }
      } else if (result.related_papers && Array.isArray(result.related_papers)) {
        responseContent = `**Related Papers** (${result.total || result.related_papers.length} found)\n\n`
        result.related_papers.forEach((paper: RelatedPaper, index: number) => {
          responseContent += `${index + 1}. **${paper.title}**\n   ${paper.authors?.slice(0, 2).join(', ')}\n   Similarity: ${(paper.similarity_score * 100).toFixed(1)}%\n\n`
        })
      } else if (result.result) {
        responseContent = `**${result.skill_name || 'Result'}**\n\n${result.result}`
      } else {
        responseContent = JSON.stringify(result, null, 2)
      }
      
      messages.value.push({
        role: 'assistant',
        content: responseContent
      })
    } else {
      messages.value.push({
        role: 'assistant',
        content: `Error: ${result.error || 'Failed to execute skill'}`
      })
    }
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const runSkillAgain = () => {
  skillExecuted.value = false
  messages.value = []
}

const backToSkills = () => {
  selectedSkill.value = null
  skillExecuted.value = false
  messages.value = []
}

const searchSuggestions = [
  'transformer attention mechanisms',
  'large language model training',
  'graph neural networks',
  'diffusion models for image generation'
]

const askSuggestions = [
  'What are the key innovations in transformer architecture?',
  'Explain the difference between BERT and GPT',
  'What is retrieval-augmented generation?',
  'How do diffusion models work?'
]

const currentSuggestions = computed(() => {
  return mode.value === 'search' ? searchSuggestions : askSuggestions
})

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      if (currentUserMessageIndex.value !== null) {
        const userMessageEl = messageRefs.value.get(currentUserMessageIndex.value)
        if (userMessageEl) {
          userMessageEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
          return
        }
      }
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async (isRetry: boolean = false) => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  if (!isRetry) {
    messages.value.push({ role: 'user', content: message })
  }
  currentUserMessageIndex.value = messages.value.length - 1
  inputMessage.value = ''
  scrollToBottom()

  isLoading.value = true
  
  try {
    if (mode.value === 'search') {
      const result = await arxivBackendAPI.semanticSearch(message, 10)
      
      messages.value.push({
        role: 'assistant',
        content: '',
        papers: result.papers.map((p: any) => ({
          id: p.id,
          title: p.title,
          abstract: p.abstract,
          authors: p.authors || [],
          primary_category: p.primary_category || '',
          categories: p.categories || [],
          published: p.published || '',
          similarity_score: p.similarity_score || 0
        })),
        model: result.model
      })
    } else {
      const result = await arxivBackendAPI.askQuestion(
        message, 
        5, 
        llmStore.selectedProvider || undefined,
        llmStore.selectedModel || undefined
      )
      
      if (result.error) {
        const configError = isConfigError(result.error)
        messages.value.push({
          role: 'assistant',
          content: `Error: ${result.error}`,
          isConfigError: configError
        })
      } else {
        messages.value.push({
          role: 'assistant',
          content: '',
          answer: result.answer,
          references: result.references || [],
          model: result.model
        })
      }
    }
  } catch (error) {
    console.error('Error:', error)
    const errorMsg = error instanceof Error ? error.message : 'Something went wrong'
    const configError = isConfigError(errorMsg)
    messages.value.push({
      role: 'assistant',
      content: `Error: ${errorMsg}`,
      isConfigError: configError
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const sendSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
  sendMessage()
}

const goToSettings = () => {
  router.push('/settings')
}

onMounted(() => {
  inputRef.value?.focus()
  if (mode.value === 'ask') {
    llmStore.init()
  }
})
</script>

<style scoped>
.assistant-page {
  padding: 88px 24px 24px 24px;
  max-width: 900px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.mode-switch {
  display: flex;
  gap: 8px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn svg {
  width: 18px;
  height: 18px;
}

.mode-btn:hover {
  border-color: #10B981;
  color: #10B981;
}

.mode-btn.active {
  background: #10B981;
  border-color: #10B981;
  color: white;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 40px;
  height: 100%;
  text-align: center;
  color: var(--text-muted);
  overflow-y: auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.skills-panel {
  width: 100%;
  max-width: 800px;
  margin-top: 24px;
}

.skills-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-muted);
}

.skills-loading .spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  text-align: left;
}

.skill-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.skill-card:hover:not(.disabled) {
  border-color: #10B981;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
}

.skill-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.skill-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #10B981, #059669);
  border-radius: 10px;
}

.skill-icon svg {
  width: 20px;
  height: 20px;
  stroke: white;
}

.skill-info {
  flex: 1;
  min-width: 0;
}

.skill-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.skill-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.skill-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.skill-category {
  flex-shrink: 0;
  font-size: 0.7rem;
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  color: var(--text-muted);
  text-transform: capitalize;
}

.skill-source {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}

.skill-source.dynamic {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.skill-source.builtin {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.skill-card.dynamic {
  border-left: 3px solid #10B981;
}

.empty-state p {
  max-width: 400px;
  margin: 0 0 24px 0;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
}

.suggestion-btn {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  border-color: #10B981;
  color: #10B981;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--accent-color);
  color: white;
}

.message.assistant .message-avatar {
  background: rgba(16, 185, 129, 0.1);
}

.message-avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  max-width: 80%;
}

.message.user .message-content {
  display: flex;
  justify-content: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.5;
}

.message.user .message-text {
  background: var(--accent-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-content:hover .message-actions {
  opacity: 1;
}

.action-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-icon-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.action-icon-btn svg {
  width: 16px;
  height: 16px;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.config-error-hint {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.settings-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settings-link-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366F1;
}

.settings-link-btn svg {
  width: 16px;
  height: 16px;
}

.papers-result {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  border-bottom-left-radius: 4px;
}

.result-header {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.paper-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.paper-card:hover {
  border-color: #10B981;
  transform: translateY(-2px);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.paper-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.similarity-score {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.paper-authors {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.paper-abstract {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.paper-meta {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
}

.paper-category {
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.paper-date {
  color: var(--text-muted);
}

.answer-result {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  border-bottom-left-radius: 4px;
}

.answer-text {
  line-height: 1.6;
  color: var(--text-primary);
}

.references {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.references h5 {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.reference-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reference-item:hover {
  background: var(--bg-tertiary);
}

.ref-title {
  flex: 1;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.ref-authors {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.ref-score {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #10B981;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.95rem;
  resize: none;
  outline: none;
  font-family: inherit;
}

.input-area textarea:focus {
  border-color: #10B981;
}

.input-area textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: #10B981;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  background: #059669;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

.skill-actions-bar {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.run-again {
  background: #10B981;
  color: white;
}

.action-btn.run-again:hover {
  background: #059669;
}

.action-btn.back-btn {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.action-btn.back-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

@media (max-width: 768px) {
  .assistant-page {
    padding: 80px 16px 16px 16px;
  }

  .message-content {
    max-width: 90%;
  }

  .suggestions {
    flex-direction: column;
  }

  .suggestion-btn {
    text-align: left;
  }

  .header-controls {
    flex-wrap: wrap;
  }
}
</style>
