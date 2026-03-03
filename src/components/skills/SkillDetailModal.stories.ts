import SkillDetailModal from '@/components/skills/SkillDetailModal.vue'
import type { Skill } from '@/types/skill'

export default {
  title: 'Components/Skills/SkillDetailModal',
  component: SkillDetailModal,
  tags: ['autodocs'],
  argTypes: {
    skill: {
      control: 'object',
      description: 'Skill data object to display'
    }
  }
}

const builtinSkill: Skill = {
  id: 'paper-summary',
  name: 'Paper Summary',
  description: 'Generate a concise summary of the paper highlighting key contributions and findings. This skill analyzes the abstract, introduction, methodology, and conclusions to provide a comprehensive overview.',
  icon: 'file-text',
  category: 'analysis',
  requires_paper: true,
  available: true,
  input_schema: null,
  source: 'builtin'
}

const dynamicSkill: Skill = {
  id: 'paper-translation',
  name: 'Paper Translation',
  description: 'Translate paper content to different languages while preserving technical terminology and formatting.',
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
      preserve_terms: {
        type: 'boolean',
        description: 'Preserve technical terms in original language',
        default: true
      },
      output_format: {
        type: 'string',
        description: 'Output format for translated content',
        enum: ['markdown', 'html', 'plain'],
        default: 'markdown'
      }
    },
    required: ['target_language']
  },
  source: 'dynamic'
}

const complexSkill: Skill = {
  id: 'literature-review',
  name: 'Literature Review Generator',
  description: 'Generate a comprehensive literature review based on multiple papers. Analyzes trends, methodologies, and findings across the selected papers.',
  icon: 'book',
  category: 'analysis',
  requires_paper: true,
  available: true,
  input_schema: {
    type: 'object',
    properties: {
      review_type: {
        type: 'string',
        description: 'Type of literature review',
        enum: ['systematic', 'narrative', 'meta-analysis'],
        default: 'systematic'
      },
      max_papers: {
        type: 'integer',
        description: 'Maximum number of papers to include',
        default: 20,
        minimum: 5,
        maximum: 100
      },
      include_citations: {
        type: 'boolean',
        description: 'Include citation information',
        default: true
      },
      focus_areas: {
        type: 'string',
        description: 'Comma-separated focus areas for the review'
      },
      output_length: {
        type: 'string',
        description: 'Target length of the review',
        enum: ['short', 'medium', 'long'],
        default: 'medium'
      }
    },
    required: ['review_type']
  },
  source: 'dynamic'
}

const unavailableSkill: Skill = {
  id: 'disabled-skill',
  name: 'Disabled Skill',
  description: 'This skill is not available due to missing dependencies or configuration issues.',
  icon: 'info',
  category: 'other',
  requires_paper: false,
  available: false,
  input_schema: null,
  source: 'builtin'
}

export const Builtin = {
  args: {
    skill: builtinSkill
  }
}

export const Dynamic = {
  args: {
    skill: dynamicSkill
  }
}

export const ComplexSchema = {
  args: {
    skill: complexSkill
  }
}

export const Unavailable = {
  args: {
    skill: unavailableSkill
  }
}

export const NoPaperRequired = {
  args: {
    skill: {
      id: 'general-qa',
      name: 'General Q&A',
      description: 'Ask general questions about research topics without requiring a specific paper.',
      icon: 'help-circle',
      category: 'assistant',
      requires_paper: false,
      available: true,
      input_schema: {
        type: 'object',
        properties: {
          question: {
            type: 'string',
            description: 'Your question about research'
          },
          context: {
            type: 'string',
            description: 'Additional context for the question'
          }
        },
        required: ['question']
      },
      source: 'builtin'
    } as Skill
  }
}

export const Null = {
  args: {
    skill: null
  }
}
