import SubAgentEditor from './SubAgentEditor.vue'

export default {
  title: 'Components/SubAgents/SubAgentEditor',
  component: SubAgentEditor,
  tags: ['autodocs'],
  argTypes: {
    agentId: {
      control: 'text',
      description: 'ID of the agent being edited'
    },
    initialContent: {
      control: 'text',
      description: 'Initial AGENT.md content'
    },
    saving: {
      control: 'boolean',
      description: 'Whether the editor is in saving state'
    }
  }
}

const validAgentContent = `---
id: research-agent
name: Research Assistant
description: Specialized in literature search and research analysis
icon: search
skills:
  - summary
  - related-papers
  - citation
tools:
  - search_papers
  - get_paper_details
  - execute_skill
max_turns: 15
temperature: 0.3
model: gpt-4o-mini
---

# Research Assistant

You are a professional research assistant specialized in helping users with academic literature search and analysis.

## Core Capabilities

1. **Literature Search**: Retrieve relevant papers based on user needs
2. **Paper Analysis**: Deeply analyze paper content and extract key information
3. **Relationship Discovery**: Identify connections between papers

## Tool Call Format

\`\`\`
[TOOL: tool_name({"arg1": "value1"})]
\`\`\`

## Available Tools

- search_papers: Search for papers
- get_paper_details: Get paper details
- execute_skill: Execute skill analysis
`

const invalidAgentContent = `---
id: test-agent
name: Test Agent
skills:
  - summary
invalid_field: this should cause an error
---

# Test Agent

This agent has invalid YAML configuration.
`

const minimalAgentContent = `---
id: minimal-agent
name: Minimal Agent
---

# Minimal Agent

A minimal agent configuration.
`

const chineseAgentContent = `---
id: chinese-agent
name: 中文助手
description: 专注于学术论文分析
icon: pen
skills:
  - summary
  - translation
tools:
  - get_paper_details
max_turns: 10
temperature: 0.5
---

# 中文助手

你是一个专业的学术论文分析助手。

## 核心能力

1. **论文摘要**: 生成论文摘要
2. **翻译**: 翻译论文内容

## 工具调用格式

\`\`\`
[TOOL: tool_name({"arg1": "value1"})]
\`\`\`
`

export const Default = {
  args: {
    agentId: 'research-agent',
    initialContent: validAgentContent,
    saving: false
  }
}

export const InvalidYaml = {
  args: {
    agentId: 'test-agent',
    initialContent: invalidAgentContent,
    saving: false
  }
}

export const Minimal = {
  args: {
    agentId: 'minimal-agent',
    initialContent: minimalAgentContent,
    saving: false
  }
}

export const Chinese = {
  args: {
    agentId: 'chinese-agent',
    initialContent: chineseAgentContent,
    saving: false
  }
}

export const Saving = {
  args: {
    agentId: 'research-agent',
    initialContent: validAgentContent,
    saving: true
  }
}

export const Empty = {
  args: {
    agentId: 'new-agent',
    initialContent: '',
    saving: false
  }
}
