<template>
  <div
    class="desktop-icon"
    :class="{
      selected: isSelected,
      dragging: isDragging,
    }"
    :style="positionStyle"
    @mousedown="$emit('mousedown', $event)"
    @dblclick="$emit('dblclick')"
    @mouseenter="$emit('mouseenter', $event)"
    @mouseleave="$emit('mouseleave')"
    @contextmenu.stop.prevent="$emit('contextmenu', $event)"
  >
    <DesktopFile
      v-if="item.type === 'file'"
      :item="item"
      :task="task"
      :is-renaming="isRenaming"
      @rename="$emit('rename', $event)"
      @rename-cancel="$emit('rename-cancel')"
    />
    <DesktopFolder
      v-else-if="item.type === 'folder'"
      :item="item"
      :is-renaming="isRenaming"
      @rename="$emit('rename', $event)"
      @rename-cancel="$emit('rename-cancel')"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDesktopStore } from '@/stores/desktop-store'
import type { DesktopItem } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'
import DesktopFile from './DesktopFile.vue'
import DesktopFolder from './DesktopFolder.vue'

const props = defineProps<{
  item: DesktopItem
  isSelected: boolean
  isDragging?: boolean
  isRenaming?: boolean
  task?: DownloadTask
}>()

const store = useDesktopStore()

defineEmits<{
  (e: 'mousedown', event: MouseEvent): void
  (e: 'dblclick'): void
  (e: 'mouseenter', event: MouseEvent): void
  (e: 'mouseleave'): void
  (e: 'contextmenu', event: MouseEvent): void
  (e: 'rename', newName: string): void
  (e: 'rename-cancel'): void
}>()

const positionStyle = computed(() => ({
  left: `${props.item.position.x}px`,
  top: `${props.item.position.y}px`,
}))
</script>

<style scoped>
.desktop-icon {
  position: absolute;
  width: var(--icon-size, 100px);
  height: var(--icon-size, 100px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
  z-index: 1;
  box-sizing: border-box;
}

.desktop-icon:hover {
  background: rgba(255, 255, 255, 0.08);
}

.desktop-icon.selected {
  background: rgba(0, 188, 212, 0.15);
  box-shadow: inset 0 0 0 2px rgba(0, 188, 212, 0.4);
}

.desktop-icon.dragging {
  opacity: 0.8;
  z-index: 1000;
  cursor: grabbing;
}
</style>
