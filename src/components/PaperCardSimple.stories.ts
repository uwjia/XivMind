import PaperCardSimple from './PaperCardSimple.vue'

export default {
  title: 'Components/PaperCardSimple',
  component: PaperCardSimple,
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
      abstract: 'We present a new object detection framework, called DETR, that leverages power of vision transformers to achieve state-of-the-art accuracy while maintaining scalability.',
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

export const WithLongTitle = {
  args: {
    paper: {
      id: '2405.12345',
      arxivId: '2405.12345',
      title: 'A Comprehensive Survey on Deep Learning Approaches for Natural Language Processing: From Word Embeddings to Large Language Models and Beyond',
      abstract: 'This survey provides an overview of deep learning techniques in NLP.',
      authors: ['Michael Brown', 'Sarah Lee', 'David Kim'],
      category: 'cs.CL',
      primaryCategory: 'cs.CL',
      categoryId: 'cs',
      categories: ['cs.CL', 'cs.AI'],
      published: '2024-05-20T00:00:00Z',
      updated: '2024-05-20T00:00:00Z',
      date: '2024-05-20T00:00:00Z',
      pdfUrl: 'https://arxiv.org/pdf/2405.12345.pdf',
      absUrl: 'https://arxiv.org/abs/2405.12345',
      citations: 87,
      downloads: 321
    },
    index: 3
  }
}

export const WithMultipleCategories = {
  args: {
    paper: {
      id: '2404.09876',
      arxivId: '2404.09876',
      title: 'Multi-Modal Learning for Vision and Language Tasks',
      abstract: 'We propose a novel multi-modal learning framework.',
      authors: ['Emily Chen', 'Robert Taylor'],
      category: 'cs.CV',
      primaryCategory: 'cs.CV',
      categoryId: 'cs',
      categories: ['cs.CV', 'cs.CL', 'cs.AI', 'cs.LG', 'cs.MM'],
      published: '2024-04-10T00:00:00Z',
      updated: '2024-04-10T00:00:00Z',
      date: '2024-04-10T00:00:00Z',
      pdfUrl: 'https://arxiv.org/pdf/2404.09876.pdf',
      absUrl: 'https://arxiv.org/abs/2404.09876',
      citations: 65,
      downloads: 289
    },
    index: 4
  }
}
