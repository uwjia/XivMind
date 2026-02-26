import ExecutionResult from './ExecutionResult.vue'
import type { SubAgentResult } from '../../types/subagent'

export default {
  title: 'Components/SubAgents/ExecutionResult',
  component: ExecutionResult,
  tags: ['autodocs'],
  argTypes: {
    result: {
      control: 'object',
      description: 'Execution result object'
    }
  }
}

const completedResult: SubAgentResult = {
  task_id: 'task-001',
  agent_id: 'research-agent',
  status: 'completed',
  output: `## Paper Analysis Summary

Based on the analysis of the provided paper, here are the key findings:

### Main Contributions
1. Novel approach to semantic search using transformer architectures
2. Improved accuracy on benchmark datasets by 15%
3. Reduced computational overhead by 40%

### Methodology
The paper introduces a new attention mechanism that focuses on relevant document sections...

### Conclusions
This work represents a significant advancement in the field of information retrieval.

[DONE]`,
  messages: [
    { role: 'user', content: 'Analyze this paper about semantic search' },
    { role: 'assistant', content: 'I will analyze the paper for you. Let me start by retrieving the details.' },
    { role: 'tool', content: 'Paper details retrieved successfully', name: 'get_paper_details' },
    { role: 'assistant', content: '## Paper Analysis Summary\n\nBased on the analysis...' }
  ],
  turns_used: 3,
  model: 'gpt-4o-mini',
  provider: 'openai'
}

const failedResult: SubAgentResult = {
  task_id: 'task-002',
  agent_id: 'analysis-agent',
  status: 'failed',
  output: '',
  messages: [
    { role: 'user', content: 'Analyze paper 2301.00001' },
    { role: 'assistant', content: 'Let me retrieve the paper details.' },
    { role: 'tool', content: 'Error: Paper not found', name: 'get_paper_details' }
  ],
  turns_used: 1,
  error: 'Failed to retrieve paper: Paper not found in database',
  model: 'gpt-4o-mini',
  provider: 'openai'
}

const runningResult: SubAgentResult = {
  task_id: 'task-003',
  agent_id: 'writer-agent',
  status: 'running',
  output: 'Processing your request...',
  messages: [
    { role: 'user', content: 'Write a literature review about machine learning' },
    { role: 'assistant', content: 'I will help you write a literature review. Let me gather relevant papers first.' }
  ],
  turns_used: 2,
  model: 'gpt-4o-mini',
  provider: 'ollama'
}

const minimalResult: SubAgentResult = {
  task_id: 'task-004',
  agent_id: 'test-agent',
  status: 'completed',
  output: 'Task completed successfully.',
  messages: [],
  turns_used: 1
}

export const Completed = {
  args: {
    result: completedResult
  }
}

export const Failed = {
  args: {
    result: failedResult
  }
}

export const Running = {
  args: {
    result: runningResult
  }
}

export const Minimal = {
  args: {
    result: minimalResult
  }
}

export const LongOutput = {
  args: {
    result: {
      ...completedResult,
      output: `## Comprehensive Analysis Report

${Array(20).fill(0).map((_, i) => `
### Section ${i + 1}
This is a detailed analysis section that demonstrates how the component handles longer content. The output should be scrollable and properly formatted.

Key points:
- Point A with detailed explanation
- Point B with supporting evidence
- Point C with conclusions
`).join('\n')}

[DONE]`
    }
  }
}
