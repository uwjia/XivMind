import AnalysisPanel from './AnalysisPanel.vue'
import type { AnalysisResult } from '@/composables/usePaperAnalysis'

export default {
  title: 'Components/paper-analysis/AnalysisPanel',
  component: AnalysisPanel,
  tags: ['autodocs'],
  argTypes: {
    paperId: {
      control: 'text',
      description: 'Paper ID to analyze'
    }
  }
}

const mockResult: AnalysisResult = {
  paper_id: '2406.04619',
  summary: 'This paper presents DETR, a new object detection framework that leverages vision transformers to achieve state-of-the-art accuracy. The approach eliminates the need for hand-designed components like non-maximum suppression and anchor generation.',
  key_points: [
    {
      title: 'Transformer Architecture',
      description: 'Uses a transformer encoder-decoder architecture for object detection, eliminating the need for hand-crafted components.',
      importance: 'high'
    },
    {
      title: 'Bipartite Matching Loss',
      description: 'Introduces a bipartite matching loss that forces unique predictions for each object.',
      importance: 'high'
    },
    {
      title: 'End-to-End Training',
      description: 'Enables end-to-end training of the object detection pipeline without requiring NMS post-processing.',
      importance: 'medium'
    }
  ],
  methodology: 'The model uses a CNN backbone for feature extraction, followed by a transformer encoder-decoder. Object queries learn to attend to different objects in the image. A bipartite matching loss ensures one-to-one prediction.',
  questions_and_conclusions: [
    {
      question: 'How does DETR compare to Faster R-CNN on small objects?',
      conclusion: 'DETR shows lower performance on small objects compared to Faster R-CNN, which is identified as a limitation of the current approach.'
    },
    {
      question: 'What is the main advantage of using transformers for object detection?',
      conclusion: 'Transformers enable direct set prediction without requiring hand-designed components like anchors and NMS, simplifying the detection pipeline.'
    }
  ],
  analyzed_at: new Date().toISOString(),
  service_used: 'openai',
  model_used: 'gpt-4'
}

export const Default = {
  args: {
    paperId: '2406.04619'
  }
}

export const WithResult = {
  args: {
    paperId: '2406.04619'
  },
  play: async ({ canvasElement }: { canvasElement: HTMLElement }) => {
    const panel = canvasElement.querySelector('.analysis-panel')
    if (panel) {
      const resultDiv = document.createElement('div')
      resultDiv.className = 'analysis-result'
      resultDiv.innerHTML = `
        <div class="result-section">
          <h4 class="section-title">Summary</h4>
          <p class="section-content">${mockResult.summary}</p>
        </div>
      `
      panel.appendChild(resultDiv)
    }
  }
}

export const Loading = {
  args: {
    paperId: '2406.04619'
  }
}

export const Error = {
  args: {
    paperId: 'invalid-paper-id'
  }
}
