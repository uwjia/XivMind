import DayTooltip from './DayTooltip.vue'

export default {
  title: 'Components/DayTooltip',
  component: DayTooltip,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Whether the tooltip is visible'
    },
    date: {
      control: 'text',
      description: 'Date string to display'
    },
    dateInfo: {
      control: 'object',
      description: 'Paper storage information'
    },
    embeddingInfo: {
      control: 'object',
      description: 'Embedding generation information'
    },
    position: {
      control: 'object',
      description: 'Tooltip position { x, y }'
    },
    closable: {
      control: 'boolean',
      description: 'Whether to show close button'
    }
  }
}

export const PapersOnly = {
  args: {
    visible: true,
    date: '2024-02-15',
    dateInfo: {
      count: 42,
      fetched_at: '2024-02-15T08:30:00Z'
    },
    embeddingInfo: null,
    position: { x: 100, y: 100 },
    closable: true
  }
}

export const EmbeddingsOnly = {
  args: {
    visible: true,
    date: '2024-02-20',
    dateInfo: null,
    embeddingInfo: {
      count: 38,
      generated_at: '2024-02-20T14:45:00Z',
      model_name: 'text-embedding-3-small'
    },
    position: { x: 150, y: 150 },
    closable: true
  }
}

export const BothInfo = {
  args: {
    visible: true,
    date: '2024-02-23',
    dateInfo: {
      count: 56,
      fetched_at: '2024-02-23T06:15:00Z'
    },
    embeddingInfo: {
      count: 56,
      generated_at: '2024-02-23T18:30:00Z',
      model_name: 'text-embedding-3-small'
    },
    position: { x: 200, y: 200 },
    closable: true
  }
}

export const WithoutModelName = {
  args: {
    visible: true,
    date: '2024-02-10',
    dateInfo: {
      count: 23,
      fetched_at: '2024-02-10T10:00:00Z'
    },
    embeddingInfo: {
      count: 23,
      generated_at: '2024-02-10T16:00:00Z'
    },
    position: { x: 120, y: 180 },
    closable: true
  }
}

export const NotClosable = {
  args: {
    visible: true,
    date: '2024-02-18',
    dateInfo: {
      count: 31,
      fetched_at: '2024-02-18T09:00:00Z'
    },
    embeddingInfo: {
      count: 31,
      generated_at: '2024-02-18T20:00:00Z',
      model_name: 'text-embedding-ada-002'
    },
    position: { x: 300, y: 250 },
    closable: false
  }
}

export const Hidden = {
  args: {
    visible: false,
    date: '2024-02-25',
    dateInfo: {
      count: 15,
      fetched_at: '2024-02-25T07:00:00Z'
    },
    embeddingInfo: null,
    position: { x: 100, y: 100 },
    closable: true
  }
}

export const InteractiveDemo = {
  render: () => ({
    components: { DayTooltip },
    setup() {
      return {}
    },
    template: `
      <div style="padding: 40px;">
        <h3 style="margin-bottom: 20px; color: var(--text-primary);">Click on a date to see the tooltip</h3>
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; max-width: 500px;">
          <div
            v-for="day in days"
            :key="day.date"
            @click="selectedDay = day"
            style="
              padding: 12px;
              text-align: center;
              border-radius: 8px;
              cursor: pointer;
              background: var(--bg-secondary);
              border: 1px solid var(--border-color);
              transition: all 0.2s;
            "
            :style="{ 
              background: selectedDay?.date === day.date ? 'var(--accent-color)' : 'var(--bg-secondary)',
              color: selectedDay?.date === day.date ? 'white' : 'var(--text-primary)'
            }"
          >
            {{ day.date.split('-')[2] }}
          </div>
        </div>
        <DayTooltip
          :visible="!!selectedDay"
          :date="selectedDay?.date || ''"
          :dateInfo="selectedDay?.dateInfo || null"
          :embeddingInfo="selectedDay?.embeddingInfo || null"
          :position="{ x: 520, y: 100 }"
          :closable="true"
          @close="selectedDay = null"
        />
      </div>
    `,
    data() {
      return {
        selectedDay: null as any,
        days: [
          { date: '2024-02-01', dateInfo: { count: 12, fetched_at: '2024-02-01T08:00:00Z' }, embeddingInfo: null },
          { date: '2024-02-02', dateInfo: { count: 28, fetched_at: '2024-02-02T08:00:00Z' }, embeddingInfo: { count: 28, generated_at: '2024-02-02T14:00:00Z', model_name: 'text-embedding-3-small' } },
          { date: '2024-02-03', dateInfo: null, embeddingInfo: null },
          { date: '2024-02-04', dateInfo: null, embeddingInfo: null },
          { date: '2024-02-05', dateInfo: { count: 45, fetched_at: '2024-02-05T08:00:00Z' }, embeddingInfo: { count: 45, generated_at: '2024-02-05T16:00:00Z' } },
          { date: '2024-02-06', dateInfo: { count: 33, fetched_at: '2024-02-06T08:00:00Z' }, embeddingInfo: null },
          { date: '2024-02-07', dateInfo: { count: 19, fetched_at: '2024-02-07T08:00:00Z' }, embeddingInfo: { count: 19, generated_at: '2024-02-07T20:00:00Z', model_name: 'text-embedding-3-large' } },
        ]
      }
    }
  })
}

export const AllVariants = {
  render: () => ({
    components: { DayTooltip },
    template: `
      <div style="padding: 40px;">
        <h3 style="margin-bottom: 30px; color: var(--text-primary);">All Tooltip Variants</h3>
        <div style="display: flex; flex-direction: column; gap: 40px;">
          <div>
            <h4 style="margin-bottom: 10px; color: var(--text-secondary);">Papers Only</h4>
            <DayTooltip
              :visible="true"
              date="2024-02-15"
              :dateInfo="{ count: 42, fetched_at: '2024-02-15T08:30:00Z' }"
              :embeddingInfo="null"
              :position="{ x: 50, y: 100 }"
              :closable="false"
            />
          </div>
          <div style="margin-top: 120px;">
            <h4 style="margin-bottom: 10px; color: var(--text-secondary);">Embeddings Only</h4>
            <DayTooltip
              :visible="true"
              date="2024-02-20"
              :dateInfo="null"
              :embeddingInfo="{ count: 38, generated_at: '2024-02-20T14:45:00Z', model_name: 'text-embedding-3-small' }"
              :position="{ x: 50, y: 260 }"
              :closable="false"
            />
          </div>
          <div style="margin-top: 120px;">
            <h4 style="margin-bottom: 10px; color: var(--text-secondary);">Both Info</h4>
            <DayTooltip
              :visible="true"
              date="2024-02-23"
              :dateInfo="{ count: 56, fetched_at: '2024-02-23T06:15:00Z' }"
              :embeddingInfo="{ count: 56, generated_at: '2024-02-23T18:30:00Z', model_name: 'text-embedding-3-small' }"
              :position="{ x: 50, y: 420 }"
              :closable="false"
            />
          </div>
        </div>
      </div>
    `
  })
}
