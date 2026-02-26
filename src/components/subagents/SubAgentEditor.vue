<template>
  <div class="subagent-editor">
    <div class="editor-header">
      <h3>Edit SubAgent Configuration</h3>
      <div class="agent-info">
        <span class="agent-id">{{ agentId }}</span>
      </div>
    </div>

    <div class="editor-body">
      <div class="editor-main">
        <div class="editor-toolbar">
          <span class="file-name">AGENT.md</span>
          <div class="toolbar-actions">
            <button 
              class="toolbar-btn" 
              @click="insertTemplate"
              :disabled="saving"
              title="Insert Template"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
            </button>
            <button 
              class="toolbar-btn" 
              @click="formatYaml"
              :disabled="saving"
              title="Format YAML"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="4 7 4 4 20 4 20 7"/>
                <line x1="9" y1="20" x2="15" y2="20"/>
                <line x1="12" y1="4" x2="12" y2="20"/>
              </svg>
            </button>
          </div>
        </div>
        <textarea
          v-model="content"
          class="code-editor"
          spellcheck="false"
          :disabled="saving"
        ></textarea>
      </div>

      <div class="editor-preview">
        <div class="preview-header">
          <span>Preview</span>
        </div>
        <div class="preview-content">
          <div v-if="parseError" class="parse-error">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>{{ parseError }}</span>
          </div>
          <div v-else-if="parsedConfig" class="parsed-config">
            <div class="config-item">
              <span class="config-label">ID:</span>
              <span class="config-value">{{ parsedConfig.id }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Name:</span>
              <span class="config-value">{{ parsedConfig.name }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Description:</span>
              <span class="config-value">{{ parsedConfig.description || '-' }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Icon:</span>
              <span class="config-value">{{ parsedConfig.icon || 'bot' }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Skills:</span>
              <div class="config-tags">
                <span v-for="skill in parsedConfig.skills" :key="skill" class="tag skill">
                  {{ skill }}
                </span>
                <span v-if="!parsedConfig.skills?.length" class="empty">-</span>
              </div>
            </div>
            <div class="config-item">
              <span class="config-label">Tools:</span>
              <div class="config-tags">
                <span v-for="tool in parsedConfig.tools" :key="tool" class="tag tool">
                  {{ tool }}
                </span>
                <span v-if="!parsedConfig.tools?.length" class="empty">-</span>
              </div>
            </div>
            <div class="config-item">
              <span class="config-label">Max Turns:</span>
              <span class="config-value">{{ parsedConfig.max_turns || 10 }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Temperature:</span>
              <span class="config-value">{{ parsedConfig.temperature || 0.7 }}</span>
            </div>
            <div class="config-item">
              <span class="config-label">Language:</span>
              <span class="config-value language-badge" :class="parsedConfig.language || 'en'">
                {{ parsedConfig.language === 'zh' ? '中文' : 'English' }}
              </span>
            </div>
            <div v-if="parsedConfig.systemPrompt" class="config-item full-width">
              <span class="config-label">System Prompt:</span>
              <div class="system-prompt-preview">{{ parsedConfig.systemPrompt }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="editor-footer">
      <button class="btn secondary" @click="$emit('cancel')" :disabled="saving">
        Cancel
      </button>
      <button 
        class="btn primary" 
        @click="handleSave"
        :disabled="saving || !hasChanges"
      >
        <svg v-if="saving" class="spinner" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4" stroke-dashoffset="10"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
        {{ saving ? 'Saving...' : 'Save' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { subagentsAPI } from '../../services/subagents'

interface ParsedConfig {
  id?: string
  name?: string
  description?: string
  icon?: string
  skills?: string[]
  tools?: string[]
  max_turns?: number
  temperature?: number
  language?: 'en' | 'zh'
  systemPrompt: string
}

const props = defineProps<{
  agentId: string
  initialContent?: string
}>()

const emit = defineEmits<{
  save: [content: string]
  cancel: []
}>()

const content = ref('')
const originalContent = ref('')
const saving = ref(false)
const parseError = ref('')

const parsedConfig = computed((): ParsedConfig | null => {
  if (!content.value) return null
  
  try {
    parseError.value = ''
    const frontmatterMatch = content.value.match(/^---\s*\n(.*?)\n---\s*\n(.*)$/s)
    
    if (!frontmatterMatch) {
      parseError.value = 'No YAML frontmatter found'
      return null
    }
    
    const yamlStr = frontmatterMatch[1]
    const systemPrompt = frontmatterMatch[2].trim()
    
    const config: Record<string, unknown> = {}
    const lines = yamlStr.split('\n')
    let currentKey = ''
    let currentArray: string[] = []
    
    for (const line of lines) {
      const arrayItemMatch = line.match(/^\s+-\s+(.+)$/)
      if (arrayItemMatch && currentKey && currentArray) {
        currentArray.push(arrayItemMatch[1].trim())
        continue
      }
      
      const keyMatch = line.match(/^(\w+):\s*(.*)$/)
      if (keyMatch) {
        if (currentKey && currentArray.length > 0) {
          config[currentKey] = currentArray
        }
        
        currentKey = keyMatch[1]
        const value = keyMatch[2].trim()
        
        if (value === '' || value === '[]') {
          currentArray = []
          config[currentKey] = []
        } else if (value.startsWith('[') && value.endsWith(']')) {
          const items = value.slice(1, -1).split(',').map(s => s.trim()).filter(Boolean)
          config[currentKey] = items
          currentArray = []
        } else {
          config[currentKey] = isNaN(Number(value)) ? value : Number(value)
          currentArray = []
        }
      }
    }
    
    if (currentKey && currentArray.length > 0) {
      config[currentKey] = currentArray
    }
    
    return {
      id: config.id as string | undefined,
      name: config.name as string | undefined,
      description: config.description as string | undefined,
      icon: config.icon as string | undefined,
      skills: config.skills as string[] | undefined,
      tools: config.tools as string[] | undefined,
      max_turns: config.max_turns as number | undefined,
      temperature: config.temperature as number | undefined,
      systemPrompt: systemPrompt || ''
    }
  } catch (e) {
    parseError.value = 'Failed to parse configuration'
    return null
  }
})

const hasChanges = computed(() => {
  return content.value !== originalContent.value
})

const loadContent = async () => {
  try {
    if (props.initialContent) {
      content.value = props.initialContent
    } else {
      const result = await subagentsAPI.getSubAgentRaw(props.agentId)
      content.value = result.content
    }
    originalContent.value = content.value
  } catch (e) {
    console.error('Failed to load agent content:', e)
  }
}

const handleSave = async () => {
  if (!hasChanges.value) return
  
  saving.value = true
  try {
    await subagentsAPI.saveSubAgent(props.agentId, content.value)
    originalContent.value = content.value
    emit('save', content.value)
  } catch (e) {
    console.error('Failed to save:', e)
  } finally {
    saving.value = false
  }
}

const insertTemplate = () => {
  const template = `---
id: ${props.agentId}
name: New SubAgent
description: Description of the SubAgent
icon: bot
skills:
  - summary
tools:
  - get_paper_details
max_turns: 10
temperature: 0.7
language: en
---

# System Prompt

You are a helpful assistant specialized in...

## Capabilities

- Capability 1
- Capability 2

## Guidelines

- Guideline 1
- Guideline 2
`
  content.value = template
}

const formatYaml = () => {
  if (!parsedConfig.value) return
  
  const config = parsedConfig.value
  const yamlLines = [
    `id: ${config.id || props.agentId}`,
    `name: ${config.name || 'SubAgent'}`,
    `description: ${config.description || ''}`,
    `icon: ${config.icon || 'bot'}`,
  ]
  
  const skills = config.skills as string[] | undefined
  if (skills?.length) {
    yamlLines.push('skills:')
    skills.forEach(s => yamlLines.push(`  - ${s}`))
  } else {
    yamlLines.push('skills: []')
  }
  
  const tools = config.tools as string[] | undefined
  if (tools?.length) {
    yamlLines.push('tools:')
    tools.forEach(t => yamlLines.push(`  - ${t}`))
  } else {
    yamlLines.push('tools: []')
  }
  
  yamlLines.push(`max_turns: ${config.max_turns || 10}`)
  yamlLines.push(`temperature: ${config.temperature || 0.7}`)
  
  content.value = `---\n${yamlLines.join('\n')}\n---\n\n${config.systemPrompt || ''}`
}

onMounted(loadContent)
</script>

<style scoped>
.subagent-editor {
  background: var(--bg-secondary);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 80vh;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.editor-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.agent-id {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-family: monospace;
}

.editor-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--border-color);
  overflow: hidden;
}

.editor-main {
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.file-name {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: monospace;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

.toolbar-btn {
  padding: 6px;
  background: none;
  border: 1px solid transparent;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-btn:hover:not(:disabled) {
  border-color: var(--border-color);
  color: var(--text-primary);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn svg {
  width: 16px;
  height: 16px;
}

.code-editor {
  flex: 1;
  padding: 12px;
  background: var(--bg-primary);
  border: none;
  color: var(--text-primary);
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.code-editor::placeholder {
  color: var(--text-muted);
}

.editor-preview {
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  overflow: hidden;
}

.preview-header {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.preview-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

.parse-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  color: #EF4444;
  font-size: 0.85rem;
}

.parse-error svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.parsed-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.config-item.full-width {
  flex-direction: column;
}

.config-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 100px;
}

.config-value {
  font-size: 0.85rem;
  color: var(--text-primary);
}

.config-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.tag.skill {
  background: rgba(0, 188, 212, 0.1);
  color: #00BCD4;
}

.tag.tool {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.empty {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.system-prompt-preview {
  margin-top: 8px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn.secondary {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn.secondary:hover:not(:disabled) {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.btn.primary {
  background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
  border: none;
  color: white;
  box-shadow: 0 0 20px rgba(0, 188, 212, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(0, 188, 212, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.language-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.language-badge.en {
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
}

.language-badge.zh {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}
</style>
