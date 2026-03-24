<template>
  <Teleport to="body">
    <div 
      class="annotation-popup"
      :style="{ left: `${position.x}px`, top: `${position.y}px` }"
      @mousedown.stop
    >
      <div class="popup-tools">
        <button 
          v-for="(colorValue, colorName) in highlightColors" 
          :key="colorName"
          class="color-tool"
          :style="{ backgroundColor: colorValue }"
          :title="`Highlight ${colorName}`"
          @click="$emit('highlight', colorName)"
        />
      </div>
      <div class="popup-actions">
        <button class="action-btn" @click="$emit('underline', currentColor)" title="Underline">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3" stroke-width="2"/>
            <line x1="4" y1="21" x2="20" y2="21" stroke-width="2"/>
          </svg>
        </button>
        <button class="action-btn" @click="$emit('strikeout', currentColor)" title="Strikethrough">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="4" y1="12" x2="20" y2="12" stroke-width="2"/>
          </svg>
        </button>
        <button class="action-btn" @click="$emit('comment')" title="Add Comment">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-width="2"/>
          </svg>
        </button>
        <button class="action-btn" @click="$emit('copy')" title="Copy">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>
          </svg>
        </button>
      </div>
      <button class="close-btn" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="18" y1="6" x2="6" y2="18" stroke-width="2"/>
          <line x1="6" y1="6" x2="18" y2="18" stroke-width="2"/>
        </svg>
      </button>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { HighlightColor } from '@/types/pdf'

defineProps<{
  position: { x: number; y: number }
  selectedText: string
  currentColor: HighlightColor
}>()

defineEmits<{
  'highlight': [color: HighlightColor]
  'underline': [color: HighlightColor]
  'strikeout': [color: HighlightColor]
  'comment': []
  'copy': []
  'close': []
}>()

const highlightColors: Record<HighlightColor, string> = {
  yellow: '#FFEB3B',
  green: '#4CAF50',
  blue: '#2196F3',
  pink: '#E91E63',
  purple: '#9C27B0',
}
</script>

<style scoped>
.annotation-popup {
  position: fixed;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translate(-50%, -100%);
  margin-top: -8px;
}

.popup-tools {
  display: flex;
  gap: 4px;
}

.color-tool {
  width: 24px;
  height: 24px;
  border: 2px solid white;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

.color-tool:hover {
  transform: scale(1.1);
}

.popup-actions {
  display: flex;
  gap: 4px;
  padding-left: 8px;
  border-left: 1px solid var(--border-color);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.close-btn svg {
  width: 16px;
  height: 16px;
}
</style>
