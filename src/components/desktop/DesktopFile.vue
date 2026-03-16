<template>
  <div class="desktop-file">
    <div class="file-icon" :class="task?.status">
      <svg viewBox="0 0 24 24" fill="none">
        <defs>
          <linearGradient id="fileGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color: #00BCD4; stop-opacity: 0.3" />
            <stop offset="100%" style="stop-color: #00ACC1; stop-opacity: 0.1" />
          </linearGradient>
        </defs>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="url(#fileGradient)" stroke="currentColor" stroke-width="1.5"/>
        <path d="M14 2v6h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="8" y1="13" x2="16" y2="13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="8" y1="16" x2="14" y2="16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <div v-if="task?.status === 'downloading'" class="progress-ring">
        <svg viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="16" fill="none" stroke="rgba(0, 188, 212, 0.2)" stroke-width="3"/>
          <circle 
            cx="18" cy="18" r="16" 
            fill="none" 
            stroke="#00BCD4" 
            stroke-width="3"
            stroke-linecap="round"
            :stroke-dasharray="100.53"
            :stroke-dashoffset="100.53 - (100.53 * (task?.progress || 0) / 100)"
            style="transform: rotate(-90deg); transform-origin: center;"
          />
        </svg>
        <span class="progress-text">{{ task?.progress || 0 }}%</span>
      </div>
      <div v-else-if="task?.status === 'completed'" class="status-badge completed">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="20 6 9 17 4 12" stroke-width="3"/>
        </svg>
      </div>
      <div v-else-if="task?.status === 'failed'" class="status-badge failed">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18" stroke-width="3"/>
          <line x1="6" y1="6" x2="18" y2="18" stroke-width="3"/>
        </svg>
      </div>
    </div>
    
    <div v-if="isRenaming" class="rename-input-wrapper">
      <input
        ref="renameInputRef"
        v-model="newName"
        type="text"
        class="rename-input"
        @keyup.enter="submitRename"
        @keyup.escape="$emit('rename-cancel')"
        @blur="submitRename"
      />
    </div>
    <div v-else class="file-name" :title="item.name">{{ item.name }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import type { DesktopItem } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'

const props = defineProps<{
  item: DesktopItem
  task?: DownloadTask
  isRenaming?: boolean
}>()

const emit = defineEmits<{
  (e: 'rename', newName: string): void
  (e: 'rename-cancel'): void
}>()

const renameInputRef = ref<HTMLInputElement | null>(null)
const newName = ref(props.item.name)

watch(() => props.isRenaming, async (isRenaming) => {
  if (isRenaming) {
    newName.value = props.item.name
    await nextTick()
    renameInputRef.value?.focus()
    renameInputRef.value?.select()
  }
})

function submitRename() {
  if (newName.value.trim() && newName.value !== props.item.name) {
    emit('rename', newName.value.trim())
  } else {
    emit('rename-cancel')
  }
}
</script>

<style scoped>
.desktop-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.file-icon {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00BCD4;
  transition: color 0.2s, transform 0.2s;
}

.file-icon:hover {
  transform: scale(1.05);
}

.file-icon svg {
  width: 100%;
  height: 100%;
}

.file-icon.completed {
  color: #00ACC1;
}

.file-icon.failed {
  color: #F44336;
}

.file-icon.downloading {
  color: #00BCD4;
}

.progress-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
}

.progress-ring svg {
  width: 100%;
  height: 100%;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 8px;
  font-weight: 600;
  color: #00BCD4;
}

.status-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-badge.completed {
  background: #00ACC1;
  color: white;
}

.status-badge.failed {
  background: #F44336;
  color: white;
}

.status-badge svg {
  width: 12px;
  height: 12px;
}

.file-name {
  font-size: 0.65rem;
  color: var(--text-primary);
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 1px 2px;
  border-radius: 4px;
  word-break: break-all;
  line-height: 1.2;
}

.rename-input-wrapper {
  width: 100%;
  padding: 0 2px;
}

.rename-input {
  width: 100%;
  font-size: 0.75rem;
  padding: 2px 4px;
  border: 1px solid var(--accent-color);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  text-align: center;
  outline: none;
}

.rename-input:focus {
  box-shadow: 0 0 0 2px rgba(0, 188, 212, 0.2);
}
</style>
