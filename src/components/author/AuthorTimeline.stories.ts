import type { Meta, StoryObj } from '@storybook/vue3'
import AuthorTimeline from './AuthorTimeline.vue'
import type { YearlyPaperCount } from '@/types/author'

const meta: Meta<typeof AuthorTimeline> = {
  title: 'Author/AuthorTimeline',
  component: AuthorTimeline,
  tags: ['autodocs'],
  argTypes: {
    yearlyPapers: {
      description: 'Array of yearly paper counts',
      control: 'object',
    },
  },
}

export default meta
type Story = StoryObj<typeof AuthorTimeline>

const sampleYearlyPapers: YearlyPaperCount[] = [
  { year: 2019, count: 5 },
  { year: 2020, count: 12 },
  { year: 2021, count: 8 },
  { year: 2022, count: 15 },
  { year: 2023, count: 22 },
  { year: 2024, count: 18 },
]

export const Default: Story = {
  args: {
    yearlyPapers: sampleYearlyPapers,
  },
}

export const SingleYear: Story = {
  args: {
    yearlyPapers: [{ year: 2024, count: 10 }],
  },
}

export const ManyYears: Story = {
  args: {
    yearlyPapers: [
      { year: 2015, count: 2 },
      { year: 2016, count: 5 },
      { year: 2017, count: 8 },
      { year: 2018, count: 12 },
      { year: 2019, count: 15 },
      { year: 2020, count: 18 },
      { year: 2021, count: 22 },
      { year: 2022, count: 25 },
      { year: 2023, count: 30 },
      { year: 2024, count: 28 },
    ],
  },
}

export const LowCounts: Story = {
  args: {
    yearlyPapers: [
      { year: 2020, count: 1 },
      { year: 2021, count: 2 },
      { year: 2022, count: 1 },
      { year: 2023, count: 3 },
      { year: 2024, count: 2 },
    ],
  },
}

export const HighCounts: Story = {
  args: {
    yearlyPapers: [
      { year: 2020, count: 50 },
      { year: 2021, count: 75 },
      { year: 2022, count: 100 },
      { year: 2023, count: 120 },
      { year: 2024, count: 95 },
    ],
  },
}

export const Empty: Story = {
  args: {
    yearlyPapers: [],
  },
}
