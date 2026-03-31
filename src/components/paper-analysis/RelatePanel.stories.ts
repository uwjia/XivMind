import RelatePanel from './RelatePanel.vue'

export default {
  title: 'Components/paper-analysis/RelatePanel',
  component: RelatePanel,
  tags: ['autodocs'],
  argTypes: {
    paperId: {
      control: 'text',
      description: 'Paper ID to find related papers for'
    },
    paperTitle: {
      control: 'text',
      description: 'Title of the paper'
    },
    paperAbstract: {
      control: 'text',
      description: 'Abstract of the paper'
    }
  }
}

export const Default = {
  args: {
    paperId: '2406.04619',
    paperTitle: 'Attention Is All You Need: Scalable and Accurate Object Detection with Transformers',
    paperAbstract: 'We present a new object detection framework, called DETR, that leverages the power of vision transformers to achieve state-of-the-art accuracy while maintaining scalability.'
  }
}

export const Loading = {
  args: {
    paperId: '2406.04619',
    paperTitle: 'Loading Test Paper',
    paperAbstract: 'This paper is still loading...'
  }
}

export const WithPapers = {
  args: {
    paperId: '2310.06825',
    paperTitle: 'Large Language Models are Zero-Shot Learners',
    paperAbstract: 'This paper explores the zero-shot learning capabilities of large language models.'
  }
}

export const NoPapers = {
  args: {
    paperId: '0000.00000',
    paperTitle: 'Obscure Paper with No Citations',
    paperAbstract: 'A very niche paper that has no related works.'
  }
}

export const Error = {
  args: {
    paperId: 'invalid-id',
    paperTitle: 'Error Test',
    paperAbstract: 'This will trigger an error.'
  }
}
