<template>
  <div 
    class="desktop-folder"
    @dragover.prevent="isDragOver = true"
    @dragleave="isDragOver = false"
    @drop.prevent="onDrop"
  >
    <div class="folder-icon" :class="{ 'drag-over': isDragOver }">
      <svg viewBox="0 0 24 24" fill="none">
        <path 
          d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C9.851 5 10.1054 5.10536 10.2929 5.29289L12 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" 
          fill="currentColor" 
          fill-opacity="0.2" 
          stroke="currentColor" 
          stroke-width="2"
        />
      </svg>
      <span v-if="childrenCount > 0" class="count-badge">
        {{ childrenCount }}
      </span>
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
    <div v-else class="folder-name" :title="item.name">{{ item.name }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { useDesktopStore } from '@/stores/desktop-store'
import type { DesktopItem } from '@/types/desktop'

const props = defineProps<{
  item: DesktopItem
  isRenaming?: boolean
}>()

const emit = defineEmits<{
  (e: 'rename', newName: string): void
  (e: 'rename-cancel'): void
}>()

const store = useDesktopStore()

const childrenCount = computed(() => {
  return store.items.filter(i => i.folderId === props.item.id).length
})
const renameInputRef = ref<HTMLInputElement | null>(null)
const newName = ref(props.item.name)
const isDragOver = ref(false)

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

function onDrop(_event: DragEvent) {
  isDragOver.value = false
  
  const draggedItemIds = store.selectedIds
  if (draggedItemIds.length === 0) return
  
  for (const id of draggedItemIds) {
    if (id !== props.item.id) {
      store.moveItemToFolder(id, props.item.id)
    }
  }
}
</script>

<style scoped>
.desktop-folder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.folder-icon {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFB74D;
  transition: all 0.2s;
}

.folder-icon svg {
  width: 100%;
  height: 100%;
}

.folder-icon.drag-over {
  color: #FFA726;
  transform: scale(1.1);
}

.count-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 9px;
  background: #FF9800;
  color: white;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.folder-name {
  font-size: 0.65rem;
  color: var(--text-primary);
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 1px 2px;
  border-radius: 4px;
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
