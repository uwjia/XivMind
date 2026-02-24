<template>
  <div class="knowledge-graph">
    <div class="graph-header">
      <h3>Knowledge Graph</h3>
      <span class="graph-date">{{ date }}</span>
    </div>
    
    <div class="graph-container" ref="graphContainer">
      <div v-if="loading" class="graph-loading">
        <div class="spinner"></div>
        <span>Building graph...</span>
      </div>
      
      <div v-else-if="error" class="graph-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>{{ error }}</span>
      </div>
      
      <div v-else-if="nodes.length === 0" class="graph-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <path d="M8 15h8M9 9h.01M15 9h.01"/>
        </svg>
        <span>No papers to display</span>
      </div>
      
      <div v-else ref="networkContainer" class="network-container"></div>
    </div>
    
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedNode" class="node-detail-overlay" @click="closeNodeDetail">
          <div class="node-detail-modal" @click.stop>
            <button class="close-btn" @click="closeNodeDetail">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            
            <div class="node-detail-content">
              <h4 class="paper-title">{{ selectedNode.paper.title }}</h4>
              
              <div class="paper-meta">
                <span class="category-badge" :style="{ background: selectedNode.color }">
                  {{ selectedNode.group }}
                </span>
                <span class="published-date">
                  {{ formatDate(selectedNode.paper.published) }}
                </span>
              </div>
              
              <div class="paper-authors">
                {{ selectedNode.paper.authors?.slice(0, 5).join(', ') }}
                <span v-if="selectedNode.paper.authors?.length > 5">
                  et al. ({{ selectedNode.paper.authors.length - 5 }} more)
                </span>
              </div>
              
              <div class="paper-abstract">
                {{ truncateAbstract(selectedNode.paper.abstract, 300) }}
              </div>
              
              <div class="paper-actions">
                <a :href="selectedNode.paper.absUrl" target="_blank" class="action-link">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                  arXiv
                </a>
                <a :href="selectedNode.paper.pdfUrl" target="_blank" class="action-link">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                  PDF
                </a>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Network } from 'vis-network/standalone'
import type { Data, Node, Edge, Options } from 'vis-network/standalone'
import { useGraphStore } from '../../stores/graph-store'
import type { GraphNode } from '../../types/graph'
import { storeToRefs } from 'pinia'

const props = defineProps<{
  date: string
}>()

const emit = defineEmits<{
  nodeClick: [node: GraphNode]
  graphReady: []
}>()

const graphStore = useGraphStore()
const { filteredNodes, filteredEdges, loading, error } = storeToRefs(graphStore)

const nodes = filteredNodes
const edges = filteredEdges

const networkContainer = ref<HTMLElement | null>(null)
const selectedNode = ref<GraphNode | null>(null)

let network: Network | null = null

const getLayoutOptions = (layoutType: string): Options => {
  const baseOptions: Options = {
    nodes: {
      shape: 'dot',
      size: 20,
      font: {
        size: 12,
        color: 'var(--text-primary)'
      },
      borderWidth: 2,
      shadow: true
    },
    edges: {
      width: 0.5,
      color: { inherit: 'from' },
      smooth: {
        enabled: true,
        type: 'continuous',
        forceDirection: 'none',
        roundness: 0.5
      }
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      zoomView: true,
      dragView: true
    }
  }

  switch (layoutType) {
    case 'circular':
      return {
        ...baseOptions,
        layout: {
          improvedLayout: true
        },
        physics: {
          stabilization: {
            iterations: 100
          },
          barnesHut: {
            gravitationalConstant: -500,
            centralGravity: 0.5,
            springLength: 150,
            springConstant: 0.02
          }
        }
      }
    case 'hierarchical':
      return {
        ...baseOptions,
        layout: {
          hierarchical: {
            enabled: true,
            direction: 'UD',
            sortMethod: 'hubsize',
            nodeSpacing: 200,
            levelSeparation: 250,
            treeSpacing: 200,
            blockShifting: true,
            edgeMinimization: true,
            parentCentralization: true
          }
        },
        physics: {
          enabled: true,
          stabilization: {
            enabled: true,
            iterations: 300
          },
          hierarchicalRepulsion: {
            nodeDistance: 250,
            damping: 0.5
          }
        },
        edges: {
          ...baseOptions.edges,
          smooth: {
            enabled: true,
            type: 'cubicBezier',
            forceDirection: 'vertical',
            roundness: 0.5
          }
        }
      }
    case 'force':
    default:
      return {
        ...baseOptions,
        physics: {
          stabilization: {
            iterations: 200
          },
          barnesHut: {
            gravitationalConstant: -2000,
            centralGravity: 0.3,
            springLength: 100,
            springConstant: 0.05
          }
        }
      }
  }
}

const initNetwork = () => {
  if (!networkContainer.value || nodes.value.length === 0) return

  const visNodes: Node[] = nodes.value.map(node => ({
    id: node.id,
    label: graphStore.config.showLabels ? node.label : '',
    title: `${node.title}\nCategory: ${node.group}`,
    group: node.group,
    value: node.value,
    color: {
      background: node.color,
      border: node.color,
      highlight: {
        background: node.color,
        border: '#fff'
      }
    }
  }))

  const visEdges: Edge[] = edges.value.map(edge => ({
    id: edge.id,
    from: edge.from,
    to: edge.to,
    value: edge.value,
    title: edge.title,
    width: Math.max(0.5, edge.value * 3)
  }))

  const data: Data = {
    nodes: visNodes,
    edges: visEdges
  }

  if (network) {
    network.destroy()
  }

  const layoutOptions = getLayoutOptions(graphStore.config.layoutType)
  network = new Network(networkContainer.value, data, layoutOptions)

  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.value.find(n => n.id === nodeId)
      if (node) {
        selectedNode.value = node
        emit('nodeClick', node)
      }
    }
  })

  network.on('doubleClick', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.value.find(n => n.id === nodeId)
      if (node?.paper?.absUrl) {
        window.open(node.paper.absUrl, '_blank')
      }
    }
  })

  emit('graphReady')
}

const closeNodeDetail = () => {
  selectedNode.value = null
}

const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const truncateAbstract = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

watch([nodes, edges], () => {
  nextTick(() => {
    initNetwork()
  })
}, { deep: true })

watch(() => graphStore.config, () => {
  nextTick(() => {
    initNetwork()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initNetwork()
  })
})

onUnmounted(() => {
  if (network) {
    network.destroy()
    network = null
  }
})
</script>

<style scoped>
.knowledge-graph {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.graph-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.graph-date {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.graph-container {
  flex: 1;
  position: relative;
  min-height: 400px;
}

.network-container {
  width: 100%;
  height: 100%;
}

.graph-loading,
.graph-error,
.graph-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: var(--text-muted);
}

.graph-loading .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.graph-error svg,
.graph-empty svg {
  width: 48px;
  height: 48px;
  stroke-width: 1.5;
}

.node-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.node-detail-modal {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--accent-color);
  color: white;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.paper-title {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  padding-right: 40px;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.category-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.published-date {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.paper-authors {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.paper-abstract {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.paper-actions {
  display: flex;
  gap: 12px;
}

.action-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-link:hover {
  background: var(--accent-color);
  color: white;
}

.action-link svg {
  width: 18px;
  height: 18px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .node-detail-modal,
.modal-leave-active .node-detail-modal {
  transition: transform 0.3s ease;
}

.modal-enter-from .node-detail-modal,
.modal-leave-to .node-detail-modal {
  transform: scale(0.9);
}
</style>
