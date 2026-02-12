// 论文类型定义
export interface Paper {
  id: string;
  arxivId?: string;
  title: string;
  authors: string[];
  abstract: string;
  primaryCategory: string;
  categories: string[];
  published: string | Date;
  updated: string | Date;
  absUrl: string;
  pdfUrl: string;
  codeUrl?: string;
  downloads?: number;
  views?: number;
  citations?: number;
  category?: string;
  summary?: string;
  links?: {
    pdf: string;
    html: string;
  };
  doi?: string;
  comment?: string;
  journalRef?: string;
  date?: string | Date;
}

// 分类类型定义
export interface Category {
  id: string;
  name: string;
}

// 日期过滤器类型定义
export interface DateFilter {
  id: string;
  name: string;
  value: string | Date;
}

// 论文获取选项类型定义
export interface FetchOptions {
  category: string;
  maxResults?: number;
  start?: number;
  sortBy?: string;
}

// 路由参数类型定义
export interface RouteParams {
  id: string;
}

// 分类颜色映射类型定义
export interface CategoryColors {
  [key: string]: string;
}

// Toast 类型定义
export type ToastType = 'success' | 'error' | 'info' | 'loading';

export interface ToastState {
  visible: boolean;
  message: string;
  type: ToastType;
  duration: number;
}

// 主题状态类型定义
export interface ThemeState {
  isDark: boolean;
}

// 侧边栏状态类型定义
export interface SidebarState {
  isCollapsed: boolean;
}

// 配置状态类型定义
export interface ConfigState {
  maxResults: number;
  useSimpleCard: boolean;
  autoRefresh: boolean;
}

// 论文状态类型定义
export interface PaperState {
  papers: Paper[];
  loading: boolean;
  error: string | null;
  selectedCategory: string;
  selectedDate: string | Date;
  currentPage: number;
  pageSize: number;
}
