<template>
  <div class="pdf-outline">
    <div v-if="outline.length === 0" class="empty-outline">
      <p>No outline available</p>
    </div>
    <div v-else class="outline-list">
      <template v-for="(item, index) in outline" :key="index">
        <OutlineItem
          :item="item"
          :level="0"
          @click="handleItemClick($event, item)"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, reactive } from 'vue'
import type { PdfOutlineItem } from '@/types/pdf'

const props = defineProps<{
  outline: PdfOutlineItem[]
}>()

const emit = defineEmits<{
  'outline-click': [item: PdfOutlineItem]
}>()

const expandedState = reactive<Record<string, boolean>>({})

function getItemId(item: PdfOutlineItem, level: number, index: number): string {
  return `${level}-${index}-${item.title}`
}

function toggleExpand(event: MouseEvent, itemId: string) {
  event.stopPropagation()
  expandedState[itemId] = !expandedState[itemId]
}

function handleItemClick(event: MouseEvent, item: PdfOutlineItem) {
  event.stopPropagation()
  emit('outline-click', item)
}

const ChevronIcon = (iconProps: { expanded: boolean }) => {
  return h('svg', {
    class: ['chevron-icon', { expanded: iconProps.expanded }],
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': '2',
    width: '12',
    height: '12',
  }, [
    h('polyline', { points: '9 18 15 12 9 6' }),
  ])
}

const BulletIcon = () => {
  return h('span', { class: 'bullet-icon' })
}

const OutlineItem = (itemProps: { item: PdfOutlineItem; level: number; index?: number }) => {
  const { item, level, index = 0 } = itemProps
  const paddingLeft = level * 20 + 12
  const hasChildren = item.items && item.items.length > 0
  const itemId = getItemId(item, level, index)
  const isExpanded = expandedState[itemId] !== false
  
  const children = []
  
  if (hasChildren) {
    children.push(
      h('div', {
        class: 'outline-item',
        style: { paddingLeft: `${paddingLeft}px` },
        onClick: (e: MouseEvent) => handleItemClick(e, item),
      }, [
        h('span', {
          class: 'expand-icon',
          onClick: (e: MouseEvent) => toggleExpand(e, itemId),
        }, [
          h(ChevronIcon, { expanded: isExpanded }),
        ]),
        h('span', { class: 'outline-title' }, item.title),
      ])
    )
    
    if (isExpanded) {
      children.push(
        h('div', { class: 'outline-children' },
          item.items.map((child, childIndex) =>
            h(OutlineItem, {
              key: childIndex,
              item: child,
              level: level + 1,
              index: childIndex,
            })
          )
        )
      )
    }
  } else {
    children.push(
      h('div', {
        class: 'outline-item',
        style: { paddingLeft: `${paddingLeft}px` },
        onClick: (e: MouseEvent) => handleItemClick(e, item),
      }, [
        h('span', { class: 'bullet-wrapper', style: { paddingLeft: `${level > 0 ? 0 : 20}px` } }, [
          level > 0 ? h(BulletIcon) : null,
        ]),
        h('span', { class: 'outline-title' }, item.title),
      ])
    )
  }
  
  return h('div', { class: 'outline-item-wrapper' }, children)
}
</script>

<style>
.pdf-outline {
  height: 100%;
  overflow-y: auto;
}

.pdf-outline .empty-outline {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.pdf-outline .outline-list {
  padding: 8px 0;
}

.pdf-outline .outline-item-wrapper {
  width: 100%;
}

.pdf-outline .outline-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  gap: 4px;
}

.pdf-outline .outline-item:hover {
  background: var(--bg-tertiary);
}

.pdf-outline .expand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.pdf-outline .expand-icon:hover {
  background: var(--bg-secondary);
}

.pdf-outline .chevron-icon {
  display: block;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.pdf-outline .chevron-icon.expanded {
  transform: rotate(90deg);
}

.pdf-outline .bullet-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.pdf-outline .bullet-icon {
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-muted);
}

.pdf-outline .outline-title {
  font-size: 13px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.pdf-outline .outline-children {
  width: 100%;
  position: relative;
}

.pdf-outline .outline-children::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--border-color);
  opacity: 0.5;
}
</style>
