interface Paper {
  id: string
  title: string
  authors: string[]
  abstract: string
  category: string
  primaryCategory: string
  categories: string[]
  date: string
  tags: string[]
  pdfUrl: string
  codeUrl: string
  citations: number
  views: number
}

interface DateFilter {
  id: string
  name: string
}

export const mockPapers: Paper[] = [
  {
    id: '2401.00001',
    title: 'DeepSeek-OCR: A Unified End-to-End Vision-Language Model for Optical Character Recognition',
    authors: ['DeepSeek Team', 'Yi Wu', 'Xiaotian Qiao'],
    abstract: 'We present DeepSeek-OCR, a unified end-to-end vision-language model designed to address long-context problems in large language models through "contextual optical compression". The model demonstrates that textual information can be efficiently compressed into visual tokens at a 7-20x ratio while maintaining high OCR accuracy. The system is based on a novel DeepEncoder architecture paired with a DeepSeek-3B-MoE decoder, achieving state-of-the-art OCR performance with significantly fewer visual tokens than existing methods.',
    category: 'cs.CV',
    primaryCategory: 'cs.CV',
    categories: ['cs.CV', 'cs.AI'],
    date: '2024-01-15',
    tags: ['OCR', 'Vision-Language Model', 'Deep Learning'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00001.pdf',
    codeUrl: 'https://github.com/deepseek-ai/deepseek-ocr',
    citations: 156,
    views: 2340
  },
  {
    id: '2401.00002',
    title: 'XivMind: Making arXiv Papers Conversational',
    authors: ['XivMind Team', 'Zhang Wei', 'Li Ming'],
    abstract: 'XivMind is an open-source toolchain built around arXiv papers with a core mission: to make any arXiv paper "questionable". Through a combination of browser extensions and backend APIs, it transforms static PDFs into "living documents" that can be fully searched, semantically queried, and experimentally reproduced with a single click. Currently, XivMind has accumulated 5k+ users in the Chrome Web Store, becoming a new standard for AI/ML researchers to browse papers daily.',
    category: 'cs.AI',
    primaryCategory: 'cs.AI',
    categories: ['cs.AI', 'cs.HC'],
    date: '2024-01-14',
    tags: ['arXiv', 'Conversational AI', 'Research Tools'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00002.pdf',
    codeUrl: 'https://github.com/XivMind/XivMind',
    citations: 89,
    views: 1567
  },
  {
    id: '2401.00003',
    title: 'Agent-Browser: AI-Driven Browser Automation',
    authors: ['Vercel Labs', 'Sarah Chen', 'John Doe'],
    abstract: 'We introduce agent-browser, an open-source project that equips AI with "flexible hands", making browser automation more convenient. It breaks the limitations of traditional automation, allowing AI to browse and operate web pages like humans without complex code, adapting to various repetitive web task scenarios. Core highlights include: precise and efficient with lower barriers, Refs system eliminating positioning challenges, Rust-based lightweight and fast, full-scenario operations with practical functionality.',
    category: 'cs.RO',
    primaryCategory: 'cs.RO',
    categories: ['cs.RO', 'cs.AI'],
    date: '2024-01-13',
    tags: ['Browser Automation', 'AI Agents', 'Rust'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00003.pdf',
    codeUrl: 'https://github.com/vercel-labs/agent-browser',
    citations: 234,
    views: 3456
  },
  {
    id: '2401.00004',
    title: 'Contextual Optical Compression for Long-Context Vision-Language Models',
    authors: ['DeepSeek Research', 'Alex Wang', 'Emma Zhang'],
    abstract: 'We propose a novel approach to handle long-context problems in vision-language models through contextual optical compression. Our method demonstrates that textual information can be efficiently compressed into visual tokens at a 7-20x ratio while maintaining high accuracy. This breakthrough significantly reduces the computational cost of processing long documents while preserving semantic information.',
    category: 'cs.CL',
    primaryCategory: 'cs.CL',
    categories: ['cs.CL', 'cs.CV'],
    date: '2024-01-12',
    tags: ['Vision-Language', 'Compression', 'Long Context'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00004.pdf',
    codeUrl: 'https://github.com/deepseek-ai/context-compression',
    citations: 67,
    views: 1234
  },
  {
    id: '2401.00005',
    title: 'Paper2Code: Automated Code Generation from Research Papers',
    authors: ['XivMind Team', 'David Lee', 'Anna Smith'],
    abstract: 'We present Paper2Code, a system that automatically generates executable code from research papers. By leveraging large language models and advanced parsing techniques, Paper2Code can extract algorithmic descriptions from papers and convert them into working code implementations. This tool significantly reduces the time researchers spend on reproducing experiments and enables faster validation of novel ideas.',
    category: 'cs.LG',
    primaryCategory: 'cs.LG',
    categories: ['cs.LG', 'cs.AI'],
    date: '2024-01-11',
    tags: ['Code Generation', 'Reproducibility', 'LLM'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00005.pdf',
    codeUrl: 'https://github.com/XivMind/paper2code',
    citations: 123,
    views: 2890
  },
  {
    id: '2401.00006',
    title: 'Immersive Translation with Full-Context Understanding',
    authors: ['DeepSeek Team', 'Michael Brown', 'Lisa Johnson'],
    abstract: 'We introduce an immersive translation system that leverages full-context understanding from thousands of related papers. The system captures research motivations, establishes connections with cutting-edge technologies, and explains key insights like a professor who has read through the entire field. Our approach significantly improves translation quality for technical content by maintaining context awareness across document boundaries.',
    category: 'cs.CL',
    primaryCategory: 'cs.CL',
    categories: ['cs.CL', 'cs.AI'],
    date: '2024-01-10',
    tags: ['Translation', 'Context Understanding', 'NLP'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00006.pdf',
    codeUrl: 'https://github.com/deepseek-ai/immersive-translation',
    citations: 45,
    views: 876
  },
  {
    id: '2401.00007',
    title: 'XivMind Browser Extension: Enhancing arXiv Experience',
    authors: ['XivMind Team', 'Chris Wilson', 'Rachel Green'],
    abstract: 'We describe the XivMind browser extension, a Chrome extension that enhances the arXiv reading experience. The extension provides features such as in-paper search, one-click access to code repositories, and aggregated discussions from GitHub Issues, Twitter threads, and Q&A platforms. With over 5,000 users, the extension has become a standard tool for AI/ML researchers.',
    category: 'cs.HC',
    primaryCategory: 'cs.HC',
    categories: ['cs.HC', 'cs.AI'],
    date: '2024-01-09',
    tags: ['Browser Extension', 'User Experience', 'arXiv'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00007.pdf',
    codeUrl: 'https://github.com/XivMind/browser-extension',
    citations: 78,
    views: 1456
  },
  {
    id: '2401.00008',
    title: 'DeepEncoder: Novel Architecture for Vision-Language Encoding',
    authors: ['DeepSeek Research', 'Kevin Park', 'Sophie Martin'],
    abstract: 'We present DeepEncoder, a novel architecture for encoding vision-language information. DeepEncoder is designed to efficiently compress textual information into visual tokens while maintaining high accuracy. The architecture achieves state-of-the-art performance on multiple OCR benchmarks with significantly fewer visual tokens than existing methods.',
    category: 'cs.CV',
    primaryCategory: 'cs.CV',
    categories: ['cs.CV', 'cs.AI'],
    date: '2024-01-08',
    tags: ['Encoder', 'Vision-Language', 'Architecture'],
    pdfUrl: 'https://arxiv.org/pdf/2401.00008.pdf',
    codeUrl: 'https://github.com/deepseek-ai/deepencoder',
    citations: 92,
    views: 1678
  }
]

export const dateFilters: DateFilter[] = [
  { id: 'all', name: 'All Time' },
  { id: '1', name: 'Last 24 Hours' },
  { id: '7', name: 'Last 7 Days' }
]
