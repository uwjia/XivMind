<template>
  <Teleport to="body">
    <div class="comment-dialog-overlay" @click="$emit('close')">
      <div class="comment-dialog" :style="{ left: `${position.x}px`, top: `${position.y}px` }" @click.stop>
        <div class="dialog-header">
          <h4>Add Comment</h4>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" stroke-width="2"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke-width="2"/>
            </svg>
          </button>
        </div>
        <div class="dialog-body">
          <textarea
            v-model="commentText"
            placeholder="Enter your comment..."
            rows="4"
            ref="textareaRef"
          ></textarea>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-primary" @click="save">Save</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps<{
  position: { x: number; y: number }
  initialContent?: string
}>()

const emit = defineEmits<{
  'save': [content: string]
  'close': []
}>()

const commentText = ref(props.initialContent || '')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function save() {
  if (commentText.value.trim()) {
    emit('save', commentText.value.trim())
  }
}

onMounted(() => {
  nextTick(() => {
    textareaRef.value?.focus()
  })
})
</script>

<style scoped>
.comment-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.3);
}

.comment-dialog {
  position: fixed;
  width: 320px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 6px;
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

.dialog-body {
  padding: 16px;
}

.dialog-body textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  resize: vertical;
  font-family: inherit;
}

.dialog-body textarea:focus {
  outline: none;
  border-color: var(--accent-color);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>
