// Paper type definition
export interface CodeUrlInfo {
  id: string;
  paperId: string;
  url: string;
  platform: string;
  owner?: string;
  repo?: string;
  isOfficial: boolean;
  stars?: number;
  language?: string;
  fetchedAt?: string;
}

export interface Paper {
  id: string;
  arxivId?: string;
  title: string;
  authors: string[];
  abstract: string;
  primaryCategory: string;
  categoryId?: string;
  category?: string;
  categories: string[];
  published: string | Date;
  updated: string | Date;
  date?: string | Date;
  absUrl: string;
  pdfUrl: string;
  codeUrl?: string;
  codeInfo?: CodeUrlInfo;
  downloads?: number;
  views?: number;
  citations?: number;
  summary?: string;
  links?: {
    pdf: string;
    html: string;
  };
  doi?: string;
  comment?: string;
  journalRef?: string;
}

export interface BackendPaper {
  id: string
  title: string
  abstract: string
  authors: string[]
  primary_category: string
  categories: string[]
  published: string
  updated: string
  pdf_url: string
  abs_url: string
  comment: string
  journal_ref: string
  doi: string
  similarity_score?: number
}

export function TransformBackendPaper(bp: BackendPaper): Paper {
  const primaryCategory = bp.primary_category || ''
  const categoryId = primaryCategory.split('.')[0] || 'cs'
  
  return {
    id: bp.id,
    arxivId: bp.id,
    title: bp.title || '',
    abstract: bp.abstract || '',
    authors: bp.authors || [],
    category: primaryCategory,
    primaryCategory: primaryCategory,
    categoryId: categoryId,
    categories: bp.categories || [],
    published: new Date(bp.published),
    updated: new Date(bp.updated),
    date: new Date(bp.published),
    pdfUrl: bp.pdf_url || '',
    absUrl: bp.abs_url || '',
    comment: bp.comment || '',
    journalRef: bp.journal_ref || '',
    doi: bp.doi || '',
    citations: Math.floor(Math.random() * 100),
    downloads: Math.floor(Math.random() * 500)
  }
}

// Category type definition
export interface Category {
  id: string;
  name: string;
}

// Date filter type definition
export interface DateFilter {
  id: string;
  name: string;
  value: string | Date;
}

// Paper fetch options type definition
export interface FetchOptions {
  category: string;
  maxResults?: number;
  start?: number;
  sortBy?: string;
}

// Route params type definition
export interface RouteParams {
  id: string;
}

// Category colors mapping type definition
export interface CategoryColors {
  [key: string]: string;
}

// Toast type definition
export type ToastType = 'success' | 'error' | 'info' | 'loading';

export interface ToastState {
  visible: boolean;
  message: string;
  type: ToastType;
  duration: number;
}

// Theme state type definition
export interface ThemeState {
  isDark: boolean;
}

// Sidebar state type definition
export interface SidebarState {
  isCollapsed: boolean;
}

// Config state type definition
export interface ConfigState {
  maxResults: number;
  useSimpleCard: boolean;
  autoRefresh: boolean;
}

// Paper state type definition
export interface PaperState {
  papers: Paper[];
  loading: boolean;
  error: string | null;
  selectedCategory: string;
  selectedDate: string | Date;
  currentPage: number;
  pageSize: number;
}
