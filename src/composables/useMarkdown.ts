import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(MarkdownItKatex, {
  throwOnError: false,
  displayMode: false
})

export function useMarkdown() {
  const render = (content: string | undefined | null): string => {
    if (!content) return ''
    return md.render(content)
  }

  const renderInline = (content: string | undefined | null): string => {
    if (!content) return ''
    return md.renderInline(content)
  }

  const renderWithDefault = (content: string | undefined | null, defaultText: string = 'No content available'): string => {
    if (!content) return `<p>${defaultText}</p>`
    return md.render(content)
  }

  return { 
    md, 
    render, 
    renderInline,
    renderWithDefault
  }
}
