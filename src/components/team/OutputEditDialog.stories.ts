import OutputEditDialog from '@/components/team/OutputEditDialog.vue'

export default {
  title: 'Components/Team/OutputEditDialog',
  component: OutputEditDialog,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: 'text',
      description: 'Markdown content to display'
    }
  }
}

const markdownContent = `# Analysis Results

## Summary
This paper introduces a novel approach to **attention mechanisms** in Vision Transformers.

### Key Findings
1. Improved accuracy on ImageNet
2. Reduced computational cost
3. Better transfer learning capabilities

## Methodology
The authors propose a \`\`\`python
def attention(query, key, value):
    scores = torch.matmul(query, key.transpose(-2, -1))
    return torch.matmul(scores, value)
\`\`\`

## Conclusion
> This work represents a significant advancement in the field.

For more details, see [the paper](https://arxiv.org).
`

export const Default = {
  args: {
    modelValue: markdownContent
  }
}

export const Empty = {
  args: {
    modelValue: ''
  }
}

export const SimpleText = {
  args: {
    modelValue: 'Just some simple text without any markdown formatting.'
  }
}

export const CodeHeavy = {
  args: {
    modelValue: `## Code Example

Here's a function:

\`\`\`typescript
interface WorkflowNode {
  id: string
  type: NodeType
  label: string
  position: { x: number; y: number }
  config: Record<string, any>
}

function createNode(type: NodeType): WorkflowNode {
  return {
    id: generateId(),
    type,
    label: getDefaultLabel(type),
    position: { x: 0, y: 0 },
    config: {}
  }
}
\`\`\`

And inline code: \`const x = 10\`
`
  }
}

export const TableContent = {
  args: {
    modelValue: `## Comparison Table

| Model | Accuracy | Speed |
|-------|----------|-------|
| ViT-B | 84.5% | Fast |
| ViT-L | 86.2% | Medium |
| ViT-H | 87.1% | Slow |

The table above shows the performance comparison.
`
  }
}
