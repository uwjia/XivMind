<template>
  <div 
    class="tooltip-wrapper" 
    @mouseenter="showTooltip" 
    @mouseleave="hideTooltip"
    ref="wrapperRef"
  >
    <slot></slot>
    <Teleport to="body">
      <Transition name="tooltip">
        <div 
          v-if="visible" 
          class="tooltip-content"
          :class="[`tooltip-${position}`, `tooltip-${type}`]"
          :style="tooltipStyle"
        >
          <span class="tooltip-text">{{ content }}</span>
          <div class="tooltip-arrow"></div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  type?: 'default' | 'info' | 'success' | 'warning'
  delay?: number
}>(), {
  position: 'top',
  type: 'default',
  delay: 200
})

const wrapperRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const tooltipStyle = ref<Record<string, string>>({})
let showTimeout: ReturnType<typeof setTimeout> | null = null

const showTooltip = async () => {
  if (!props.content) return
  
  showTimeout = setTimeout(async () => {
    visible.value = true
    await nextTick()
    updatePosition()
  }, props.delay)
}

const hideTooltip = () => {
  if (showTimeout) {
    clearTimeout(showTimeout)
    showTimeout = null
  }
  visible.value = false
}

const updatePosition = () => {
  if (!wrapperRef.value) return
  
  const rect = wrapperRef.value.getBoundingClientRect()
  const gap = 8
  
  switch (props.position) {
    case 'top':
      tooltipStyle.value = {
        left: `${rect.left + rect.width / 2}px`,
        top: `${rect.top - gap}px`,
        transform: 'translate(-50%, -100%)'
      }
      break
    case 'bottom':
      tooltipStyle.value = {
        left: `${rect.left + rect.width / 2}px`,
        top: `${rect.bottom + gap}px`,
        transform: 'translate(-50%, 0)'
      }
      break
    case 'left':
      tooltipStyle.value = {
        left: `${rect.left - gap}px`,
        top: `${rect.top + rect.height / 2}px`,
        transform: 'translate(-100%, -50%)'
      }
      break
    case 'right':
      tooltipStyle.value = {
        left: `${rect.right + gap}px`,
        top: `${rect.top + rect.height / 2}px`,
        transform: 'translate(0, -50%)'
      }
      break
  }
}
</script>

<style scoped>
.tooltip-wrapper {
  display: inline-block;
}

.tooltip-content {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
}

.tooltip-text {
  display: block;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tooltip-arrow {
  position: absolute;
  width: 8px;
  height: 8px;
  transform: rotate(45deg);
}

.tooltip-default .tooltip-text {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.tooltip-default .tooltip-arrow {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.tooltip-info .tooltip-text {
  background: linear-gradient(135deg, var(--accent-color) 0%, #764ba2 100%);
  color: white;
  border: none;
}

.tooltip-info .tooltip-arrow {
  background: var(--accent-color);
  border: none;
}

.tooltip-success .tooltip-text {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
  border: none;
}

.tooltip-success .tooltip-arrow {
  background: #43e97b;
  border: none;
}

.tooltip-warning .tooltip-text {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
  border: none;
}

.tooltip-warning .tooltip-arrow {
  background: #fa709a;
  border: none;
}

.tooltip-top .tooltip-arrow {
  bottom: -5px;
  left: 50%;
  margin-left: -4px;
  border-top: none;
  border-left: none;
}

.tooltip-bottom .tooltip-arrow {
  top: -5px;
  left: 50%;
  margin-left: -4px;
  border-bottom: none;
  border-right: none;
}

.tooltip-left .tooltip-arrow {
  right: -5px;
  top: 50%;
  margin-top: -4px;
  border-left: none;
  border-bottom: none;
}

.tooltip-right .tooltip-arrow {
  left: -5px;
  top: 50%;
  margin-top: -4px;
  border-right: none;
  border-top: none;
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
}

.tooltip-top.tooltip-enter-from,
.tooltip-top.tooltip-leave-to {
  transform: translate(-50%, calc(-100% + 4px));
}

.tooltip-bottom.tooltip-enter-from,
.tooltip-bottom.tooltip-leave-to {
  transform: translate(-50%, -4px);
}

.tooltip-left.tooltip-enter-from,
.tooltip-left.tooltip-leave-to {
  transform: translate(calc(-100% + 4px), -50%);
}

.tooltip-right.tooltip-enter-from,
.tooltip-right.tooltip-leave-to {
  transform: translate(-4px, -50%);
}
</style>
