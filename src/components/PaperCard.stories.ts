import PaperCard from './PaperCard.vue'

export default {
  title: 'Components/PaperCard',
  component: PaperCard,
  tags: ['autodocs'],
  argTypes: {
    paper: {
      control: 'object',
      description: 'Paper data object'
    },
    index: {
      control: 'number',
      description: 'Paper index number'
    }
  }
}

export const Default = {
  args: {
    paper: {
      id: '2406.04619',
      arxivId: '2406.04619',
      title: 'Attention Is All You Need: Scalable and Accurate Object Detection with Transformers',
      abstract: 'We present a new object detection framework, called DETR, that leverages the power of vision transformers to achieve state-of-the-art accuracy while maintaining scalability.',
      authors: ['John Doe', 'Jane Smith'],
      category: 'cs.AI',
      primaryCategory: 'cs.AI',
      categoryId: 'cs',
      categories: ['cs.AI', 'cs.CV', 'cs.LG'],
      published: '2024-06-01T00:00:00Z',
      updated: '2024-06-01T00:00:00Z',
      date: '2024-06-01T00:00:00Z',
      pdfUrl: 'https://arxiv.org/pdf/2406.04619.pdf',
      absUrl: 'https://arxiv.org/abs/2406.04619',
      citations: 42,
      downloads: 156
    },
    index: 1
  }
}

export const WithHighCitations = {
  args: {
    paper: {
      id: '2310.06825',
      arxivId: '2310.06825',
      title: 'Large Language Models are Zero-Shot Learners',
      abstract: 'This paper explores the zero-shot learning capabilities of large language models.',
      authors: ['Alice Johnson', 'Bob Wilson'],
      category: 'cs.AI',
      primaryCategory: 'cs.AI',
      categoryId: 'cs',
      categories: ['cs.AI', 'cs.CL'],
      published: '2024-01-15T00:00:00Z',
      updated: '2024-01-15T00:00:00Z',
      date: '2024-01-15T00:00:00Z',
      pdfUrl: 'https://arxiv.org/pdf/2310.06825.pdf',
      absUrl: 'https://arxiv.org/abs/2310.06825',
      citations: 128,
      downloads: 542
    },
    index: 2
  }
}