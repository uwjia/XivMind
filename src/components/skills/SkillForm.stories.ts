import SkillForm from './SkillForm.vue'
import type { Skill } from '../../types/skill'

export default {
  title: 'Components/Skills/SkillForm',
  component: SkillForm,
  tags: ['autodocs'],
  argTypes: {
    skill: {
      control: 'object',
      description: 'Skill data object with input schema'
    }
  }
}

const simpleSkill: Skill = {
  id: 'paper-summary',
  name: 'Paper Summary',
  description: 'Generate a concise summary of the paper highlighting key contributions and findings',
  icon: 'file-text',
  category: 'analysis',
  requires_paper: true,
  available: true,
  input_schema: null,
  source: 'builtin'
}

const translationSkill: Skill = {
  id: 'paper-translation',
  name: 'Paper Translation',
  description: 'Translate paper content to different languages',
  icon: 'languages',
  category: 'writing',
  requires_paper: true,
  available: true,
  input_schema: {
    type: 'object',
    properties: {
      target_language: {
        type: 'string',
        description: 'Target language for translation',
        enum: ['Chinese', 'Japanese', 'German', 'French', 'Spanish'],
        default: 'Chinese'
      },
      content_type: {
        type: 'string',
        description: 'Which content to translate',
        enum: ['abstract', 'full', 'title'],
        default: 'abstract'
      }
    },
    required: []
  },
  source: 'dynamic'
}

const complexSkill: Skill = {
  id: 'advanced-analysis',
  name: 'Advanced Paper Analysis',
  description: 'Perform comprehensive analysis with multiple parameters',
  icon: 'file-text',
  category: 'analysis',
  requires_paper: true,
  available: true,
  input_schema: {
    type: 'object',
    properties: {
      analysis_depth: {
        type: 'integer',
        description: 'Depth of analysis (1-10)',
        default: 5,
        minimum: 1,
        maximum: 10
      },
      include_references: {
        type: 'boolean',
        description: 'Include reference analysis'
      },
      output_format: {
        type: 'string',
        description: 'Output format',
        enum: ['markdown', 'json', 'html'],
        default: 'markdown'
      },
      custom_prompt: {
        type: 'string',
        description: 'Custom analysis prompt'
      }
    },
    required: ['analysis_depth']
  },
  source: 'dynamic'
}

const noPaperRequiredSkill: Skill = {
  id: 'bulk-export',
  name: 'Bulk Export',
  description: 'Export multiple papers in various formats',
  icon: 'file-text',
  category: 'utility',
  requires_paper: false,
  available: true,
  input_schema: {
    type: 'object',
    properties: {
      format: {
        type: 'string',
        description: 'Export format',
        enum: ['csv', 'json', 'bibtex'],
        default: 'csv'
      },
      include_abstract: {
        type: 'boolean',
        description: 'Include abstracts in export'
      }
    },
    required: []
  },
  source: 'builtin'
}

export const Simple = {
  args: {
    skill: simpleSkill
  }
}

export const Translation = {
  args: {
    skill: translationSkill
  }
}

export const ComplexForm = {
  args: {
    skill: complexSkill
  }
}

export const NoPaperRequired = {
  args: {
    skill: noPaperRequiredSkill
  }
}

export const FormStates = {
  render: () => ({
    components: { SkillForm },
    setup() {
      return { simpleSkill, translationSkill, complexSkill }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 24px; max-width: 600px;">
        <div>
          <h4 style="margin-bottom: 12px; color: #666;">Simple Form (Paper Required)</h4>
          <SkillForm :skill="simpleSkill" />
        </div>
        <div>
          <h4 style="margin-bottom: 12px; color: #666;">Translation Form (With Enums)</h4>
          <SkillForm :skill="translationSkill" />
        </div>
        <div>
          <h4 style="margin-bottom: 12px; color: #666;">Complex Form (Multiple Field Types)</h4>
          <SkillForm :skill="complexSkill" />
        </div>
      </div>
    `
  })
}
