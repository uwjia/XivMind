declare module 'markdown-it-katex' {
  import MarkdownIt from 'markdown-it'
  
  interface MarkdownItKatexOptions {
    throwOnError?: boolean
    errorColor?: string
    displayMode?: boolean
    trust?: boolean
    fleqn?: boolean
    globalGroup?: boolean
    maxSize?: number
    maxExpand?: number
    strict?: boolean | string
    macros?: Record<string, string>
    colorIsTextColor?: boolean
    minRuleThickness?: number
    maxRuleThickness?: number
  }
  
  function markdownItKatex(md: MarkdownIt, options?: MarkdownItKatexOptions): void
  
  export default markdownItKatex
}
