<template>
  <div v-if="hasResult" class="node-preview" :class="{ expanded, error: !!error }">
    <div class="preview-header" @click="toggleExpand">
      <span class="preview-label">{{ error ? 'Error' : 'Result' }}</span>
      <span class="preview-toggle">{{ expanded ? '▼' : '▶' }}</span>
    </div>
    <div v-if="expanded" class="preview-content">
      <div v-if="error" class="error-result">
        {{ error }}
      </div>
      <div v-else-if="isTextResult" class="text-result">
        {{ truncatedText }}
        <button v-if="needsTruncation" class="show-more" @click="showFullResult">
          Show full result
        </button>
      </div>
      <div v-else-if="isObjectResult" class="json-result">
        <pre>{{ formattedJson }}</pre>
      </div>
      <div v-else class="unknown-result">
        {{ result }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  result?: any
  error?: string
}>()

const expanded = ref(true)
const maxLength = 200

const hasResult = computed(() => {
  return props.result !== undefined && props.result !== null || !!props.error
})

const isTextResult = computed(() => {
  return typeof props.result === 'string'
})

const isObjectResult = computed(() => {
  return typeof props.result === 'object' && !Array.isArray(props.result)
})

const truncatedText = computed(() => {
  if (!isTextResult.value) return ''
  const text = props.result as string
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
})

const needsTruncation = computed(() => {
  if (!isTextResult.value) return false
  return (props.result as string).length > maxLength
})

const formattedJson = computed(() => {
  if (!isObjectResult.value) return ''
  return JSON.stringify(props.result, null, 2)
})

function toggleExpand() {
  expanded.value = !expanded.value
}

function showFullResult() {
  expanded.value = true
}
</script>

<style scoped>
.node-preview {
  margin-top: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-tertiary);
  overflow: hidden;
  font-size: 0.75rem;
}

.node-preview.error {
  border-color: #EF4444;
}

.node-preview.error .preview-header {
  background: rgba(239, 68, 68, 0.1);
}

.node-preview.error .preview-label {
  color: #EF4444;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  cursor: pointer;
  background: var(--bg-secondary);
}

.preview-header:hover {
  background: var(--bg-primary);
}

.preview-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.preview-toggle {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.preview-content {
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.preview-content::-webkit-scrollbar {
  width: 4px;
}

.preview-content::-webkit-scrollbar-track {
  background: transparent;
}

.preview-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 2px;
}

.error-result {
  color: #EF4444;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.text-result {
  color: var(--text-primary);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.json-result {
  overflow-x: auto;
}

.json-result pre {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 0.7rem;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.unknown-result {
  color: var(--text-muted);
}

.show-more {
  display: block;
  margin-top: 8px;
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--primary-color);
  font-size: 0.7rem;
  cursor: pointer;
}

.show-more:hover {
  background: var(--bg-secondary);
}
</style>
