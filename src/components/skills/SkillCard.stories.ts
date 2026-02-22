import SkillCard from './SkillCard.vue'
import type { Skill } from '../../types/skill'

export default {
  title: 'Components/Skills/SkillCard',
  component: SkillCard,
  tags: ['autodocs'],
  argTypes: {
    skill: {
      control: 'object',
      description: 'Skill data object'
    },
    selected: {
      control: 'boolean',
      description: 'Whether the skill is selected'
    },
    showActions: {
      control: 'boolean',
      description: 'Whether to show action buttons'
    }
  }
}

const defaultSkill: Skill = {
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

const dynamicSkill: Skill = {
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
      }
    },
    required: []
  },
  source: 'dynamic'
}

const unavailableSkill: Skill = {
  id: 'disabled-skill',
  name: 'Disabled Skill',
  description: 'This skill is not available due to missing dependencies',
  icon: 'info',
  category: 'other',
  requires_paper: false,
  available: false,
  input_schema: null,
  source: 'builtin'
}

export const Default = {
  args: {
    skill: defaultSkill
  }
}

export const Dynamic = {
  args: {
    skill: dynamicSkill
  }
}

export const Unavailable = {
  args: {
    skill: unavailableSkill
  }
}

export const Selected = {
  args: {
    skill: defaultSkill,
    selected: true
  }
}

export const WithActions = {
  args: {
    skill: dynamicSkill,
    showActions: true
  }
}

export const DynamicWithActions = {
  args: {
    skill: dynamicSkill,
    showActions: true
  }
}

export const AllVariants = {
  render: () => ({
    components: { SkillCard },
    setup() {
      const skills: Skill[] = [
        { ...defaultSkill, id: 'summary-1', name: 'Paper Summary', icon: 'file-text' },
        { ...dynamicSkill, id: 'translation-1', name: 'Translation', icon: 'languages' },
        { 
          id: 'citation-1',
          name: 'Generate Citation',
          description: 'Generate citations in various formats (BibTeX, APA, MLA)',
          icon: 'quote',
          category: 'writing',
          requires_paper: true,
          available: true,
          input_schema: null,
          source: 'builtin'
        },
        {
          id: 'related-1',
          name: 'Find Related Papers',
          description: 'Find papers related to the current paper',
          icon: 'search',
          category: 'analysis',
          requires_paper: true,
          available: true,
          input_schema: null,
          source: 'dynamic'
        }
      ]
      return { skills }
    },
    template: `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; max-width: 800px;">
        <SkillCard 
          v-for="skill in skills" 
          :key="skill.id" 
          :skill="skill"
          :show-actions="skill.source === 'dynamic'"
        />
      </div>
    `
  })
}
