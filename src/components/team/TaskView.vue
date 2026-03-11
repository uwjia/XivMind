<template>
  <div class="task-view">
    <div class="task-input-section">
      <div class="section-header">
        <h2>New Task</h2>
        <div class="header-actions">
          <button 
            class="workflow-btn"
            @click="$emit('change-view', 'workflow')"
            title="Switch to Workflow View"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
            </svg>
            <span>Workflow</span>
          </button>
          <div class="mode-toggle">
            <button 
              :class="['toggle-btn', { active: !forceTeamMode }]"
              @click="forceTeamMode = false"
            >
              Auto
            </button>
            <button 
              :class="['toggle-btn', { active: forceTeamMode }]"
              @click="forceTeamMode = true"
            >
              Force Team
            </button>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <textarea
          v-model="instruction"
          placeholder="Enter your research task... e.g., 'Compare the attention mechanisms in Vision Transformers and BERT'"
          rows="4"
        ></textarea>
        
        <div class="input-options">
          <div class="option-group">
            <label>Paper IDs (optional)</label>
            <input
              v-model="paperIdsStr"
              type="text"
              placeholder="e.g., 2301.00001, 2301.00002"
            />
          </div>
        </div>
        
        <div class="action-buttons">
          <button 
            class="btn secondary" 
            @click="handleAnalyze" 
            :disabled="analyzing || !instruction.trim()"
          >
            {{ analyzing ? 'Analyzing...' : 'Analyze' }}
          </button>
          <button 
            class="btn primary" 
            @click="handleExecute" 
            :disabled="executing || !instruction.trim()"
          >
            {{ executing ? 'Executing...' : 'Execute' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="analysisResult" class="analysis-section">
      <div class="section-header">
        <h2>Task Analysis</h2>
        <span 
          class="complexity-badge" 
          :style="{ backgroundColor: getComplexityColor(analysisResult.complexity) }"
        >
          {{ analysisResult.complexity }}
        </span>
      </div>
      
      <div class="analysis-content">
        <div class="analysis-item">
          <span class="label">Team Mode:</span>
          <span class="value">{{ analysisResult.use_team_mode ? 'Yes' : 'No (Single Agent)' }}</span>
        </div>
        <div class="analysis-item">
          <span class="label">Reasoning:</span>
          <span class="value">{{ analysisResult.reasoning }}</span>
        </div>
        
        <div v-if="analysisResult.subtasks.length > 0" class="subtasks-preview">
          <h4>Subtasks ({{ analysisResult.subtasks.length }})</h4>
          <div class="subtask-list">
            <div 
              v-for="(subtask, index) in analysisResult.subtasks" 
              :key="index"
              class="subtask-item"
            >
              <span class="subtask-index">{{ index + 1 }}</span>
              <div class="subtask-info">
                <span class="subtask-agent">{{ subtask.assigned_agent }}</span>
                <span class="subtask-instruction">{{ subtask.instruction }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="currentResult" class="result-section">
      <div class="section-header">
        <h2>Execution Result</h2>
        <span 
          class="status-badge" 
          :style="{ backgroundColor: getStatusColor(currentResult.status) }"
        >
          {{ currentResult.status }}
        </span>
      </div>
      
      <div class="result-stats">
        <div class="stat-item">
          <span class="stat-value">{{ currentResult.total_subtasks }}</span>
          <span class="stat-label">Total</span>
        </div>
        <div class="stat-item success">
          <span class="stat-value">{{ currentResult.completed_subtasks }}</span>
          <span class="stat-label">Completed</span>
        </div>
        <div class="stat-item error">
          <span class="stat-value">{{ currentResult.failed_subtasks }}</span>
          <span class="stat-label">Failed</span>
        </div>
      </div>

      <div v-if="currentResult.output" class="output-area">
        <h4>Output</h4>
        <div class="output-content" v-html="formatOutput(currentResult.output)"></div>
      </div>

      <div v-if="currentResult.error" class="error-area">
        <h4>Error</h4>
        <p>{{ currentResult.error }}</p>
      </div>

      <div v-if="currentResult.subtask_results?.length > 0" class="subtask-results">
        <h4>Subtask Results</h4>
        <div class="result-list">
          <details 
            v-for="result in currentResult.subtask_results" 
            :key="result.subtask_id"
            class="result-item"
          >
            <summary>
              <span 
                class="result-status"
                :style="{ color: getStatusColor(result.status) }"
              >
                {{ getSubTaskStatusIcon(result.status) }}
              </span>
              <span class="result-agent">{{ result.agent_id }}</span>
              <span class="result-id">{{ result.subtask_id }}</span>
            </summary>
            <div class="result-content">
              <p v-if="result.result">{{ result.result }}</p>
              <p v-if="result.error" class="error">{{ result.error }}</p>
            </div>
          </details>
        </div>
      </div>
    </div>

    <div v-if="stats" class="stats-section">
      <div class="section-header">
        <h2>System Stats</h2>
      </div>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">⚡</span>
          <div class="stat-info">
            <span class="stat-value">{{ stats.initialized ? 'Ready' : 'Not Ready' }}</span>
            <span class="stat-label">Status</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📊</span>
          <div class="stat-info">
            <span class="stat-value">{{ stats.orchestrator_stats?.active_sessions || 0 }}</span>
            <span class="stat-label">Active Sessions</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🤖</span>
          <div class="stat-info">
            <span class="stat-value">{{ stats.available_agents?.length || 0 }}</span>
            <span class="stat-label">Available Agents</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeam } from '@/composables/useTeam'
import type { TeamExecuteRequest } from '@/types/team'

const {
  executing,
  analyzing,
  currentResult,
  analysisResult,
  stats,
  analyzeTask,
  executeTask,
  loadStats,
  getStatusColor,
  getComplexityColor,
  getSubTaskStatusIcon,
} = useTeam()

const instruction = ref('')
const paperIdsStr = ref('')
const forceTeamMode = ref(false)

const emit = defineEmits<{
  (e: 'notify', type: string, message: string): void
  (e: 'change-view', view: 'task' | 'workflow'): void
}>()

const handleAnalyze = async () => {
  if (!instruction.value.trim()) return
  
  const paperIds = paperIdsStr.value
    .split(',')
    .map(id => id.trim())
    .filter(Boolean)
  
  const request: TeamExecuteRequest = {
    instruction: instruction.value.trim(),
    paper_ids: paperIds.length > 0 ? paperIds : undefined,
    force_team_mode: forceTeamMode.value,
  }
  
  const result = await analyzeTask(request)
  
  if (result) {
    emit('notify', 'success', 'Task analyzed successfully')
  }
}

const handleExecute = async () => {
  if (!instruction.value.trim()) return
  
  const paperIds = paperIdsStr.value
    .split(',')
    .map(id => id.trim())
    .filter(Boolean)
  
  const request: TeamExecuteRequest = {
    instruction: instruction.value.trim(),
    paper_ids: paperIds.length > 0 ? paperIds : undefined,
    force_team_mode: forceTeamMode.value,
  }
  
  const result = await executeTask(request)
  
  if (result) {
    emit('notify', 'success', 'Task executed successfully')
  }
}

const formatOutput = (output: string): string => {
  return output
    .replace(/\n/g, '<br>')
    .replace(/#{1,6}\s*(.+)/g, '<strong>$1</strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.task-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.task-input-section,
.analysis-section,
.result-section,
.stats-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  color: #8B5CF6;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.workflow-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.workflow-btn svg {
  width: 16px;
  height: 16px;
}

.mode-toggle {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 4px;
}

.toggle-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-area textarea {
  width: 100%;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  resize: vertical;
  min-height: 100px;
}

.input-area textarea:focus {
  outline: none;
  border-color: #8B5CF6;
}

.input-options {
  display: flex;
  gap: 16px;
}

.option-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-group label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.option-group input {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.option-group input:focus {
  outline: none;
  border-color: #8B5CF6;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn.secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn.secondary:hover:not(:disabled) {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.btn.primary {
  background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
  border: none;
  color: white;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.5);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.complexity-badge,
.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
  text-transform: uppercase;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-item {
  display: flex;
  gap: 8px;
}

.analysis-item .label {
  color: var(--text-muted);
  min-width: 100px;
}

.analysis-item .value {
  color: var(--text-primary);
}

.subtasks-preview {
  margin-top: 16px;
}

.subtasks-preview h4 {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.subtask-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtask-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.subtask-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #8B5CF6;
  color: white;
  border-radius: 50%;
  font-size: 0.8rem;
  font-weight: 600;
}

.subtask-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.subtask-agent {
  font-size: 0.8rem;
  color: #8B5CF6;
  font-weight: 500;
}

.subtask-instruction {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.result-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.stat-item .stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-item .stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.stat-item.success .stat-value {
  color: #10B981;
}

.stat-item.error .stat-value {
  color: #EF4444;
}

.output-area {
  margin-bottom: 24px;
}

.output-area h4 {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.output-content {
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  color: var(--text-primary);
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.error-area {
  margin-bottom: 24px;
}

.error-area h4 {
  margin: 0 0 12px 0;
  color: #EF4444;
  font-size: 0.9rem;
}

.error-area p {
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  color: #EF4444;
}

.subtask-results h4 {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.result-item summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  list-style: none;
}

.result-item summary::-webkit-details-marker {
  display: none;
}

.result-status {
  font-size: 1.2rem;
}

.result-agent {
  color: #8B5CF6;
  font-weight: 500;
}

.result-id {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.result-content {
  padding: 0 12px 12px 44px;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.result-content .error {
  color: #EF4444;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-card .stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-card .stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
