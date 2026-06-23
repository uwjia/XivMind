export interface Category {
  id: string
  name: string
}

export interface CategoryGroup {
  id: string
  name: string
  wildcard: string
  categories: Category[]
  colors: Record<string, string>
  color: string
}

// Computer Science categories
export const CATEGORY_IDS: string[] = [
  'cs.AI', 'cs.LG', 'cs.CV', 'cs.AR', 'cs.CL', 'cs.CC', 'cs.CE', 'cs.CG', 'cs.CR', 'cs.CY',
  'cs.DB', 'cs.DC', 'cs.DL', 'cs.DM', 'cs.DS', 'cs.ET', 'cs.FL', 'cs.GL', 'cs.GR', 'cs.GT',
  'cs.HC', 'cs.IR', 'cs.IT', 'cs.LO', 'cs.MA', 'cs.MM', 'cs.MS', 'cs.NA', 'cs.NE', 'cs.NI',
  'cs.OH', 'cs.OS', 'cs.PL', 'cs.PF', 'cs.RO', 'cs.SC', 'cs.SD', 'cs.SE', 'cs.SI', 'cs.SY',
]

export const categories: Category[] = [
  { id: 'cs*', name: 'All Computer Science' },
  { id: 'cs.AI', name: 'Artificial Intelligence' },
  { id: 'cs.LG', name: 'Machine Learning' },
  { id: 'cs.CV', name: 'Computer Vision and Pattern Recognition' },
  { id: 'cs.AR', name: 'Hardware Architecture' },
  { id: 'cs.CL', name: 'Computation and Language' },
  { id: 'cs.CC', name: 'Computational Complexity' },
  { id: 'cs.CE', name: 'Computational Engineering, Finance, and Science' },
  { id: 'cs.CG', name: 'Computational Geometry' },
  { id: 'cs.GT', name: 'Computer Science and Game Theory' },
  { id: 'cs.CY', name: 'Computers and Society' },
  { id: 'cs.CR', name: 'Cryptography and Security' },
  { id: 'cs.DS', name: 'Data Structures and Algorithms' },
  { id: 'cs.DB', name: 'Databases' },
  { id: 'cs.DL', name: 'Digital Libraries' },
  { id: 'cs.DM', name: 'Discrete Mathematics' },
  { id: 'cs.DC', name: 'Distributed, Parallel, and Cluster Computing' },
  { id: 'cs.ET', name: 'Emerging Technologies' },
  { id: 'cs.FL', name: 'Formal Languages and Automata Theory' },
  { id: 'cs.GL', name: 'General Literature' },
  { id: 'cs.GR', name: 'Graphics' },
  { id: 'cs.HC', name: 'Human-Computer Interaction' },
  { id: 'cs.IR', name: 'Information Retrieval' },
  { id: 'cs.IT', name: 'Information Theory' },
  { id: 'cs.LO', name: 'Logic in Computer Science' },
  { id: 'cs.MA', name: 'Multiagent Systems' },
  { id: 'cs.MM', name: 'Multimedia' },
  { id: 'cs.MS', name: 'Mathematical Software' },
  { id: 'cs.NA', name: 'Numerical Analysis' },
  { id: 'cs.NE', name: 'Neural and Evolutionary Computing' },
  { id: 'cs.NI', name: 'Networking and Internet Architecture' },
  { id: 'cs.OH', name: 'Other Computer Science' },
  { id: 'cs.OS', name: 'Operating Systems' },
  { id: 'cs.PL', name: 'Programming Languages' },
  { id: 'cs.RO', name: 'Robotics' },
  { id: 'cs.SC', name: 'Symbolic Computation' },
  { id: 'cs.SD', name: 'Sound and Music Computing' },
  { id: 'cs.SE', name: 'Software Engineering' },
  { id: 'cs.SI', name: 'Social and Information Networks' },
  { id: 'cs.SY', name: 'Systems and Control' },
]

export const categoryColors: Record<string, string> = {
  'cs.AI': '#4CAF50',
  'cs.CL': '#2196F3',
  'cs.CV': '#FF9800',
  'cs.LG': '#9C27B0',
  'cs.NE': '#F44336',
  'cs.CR': '#3F51B5',
  'cs.DC': '#00BCD4',
  'cs.DB': '#FFC107',
  'cs.DL': '#607D8B',
  'cs.DS': '#795548',
  'cs.ET': '#E91E63',
  'cs.FL': '#009688',
  'cs.GL': '#673AB7',
  'cs.GR': '#33691E',
  'cs.AR': '#BF360C',
  'cs.HC': '#00ACC1',
  'cs.IR': '#FF6F00',
  'cs.IT': '#536DFE',
  'cs.LO': '#00897B',
  'cs.MS': '#4527A0',
  'cs.MM': '#D81B60',
  'cs.NI': '#2E7D32',
  'cs.OH': '#6D4C41',
  'cs.OS': '#1976D2',
  'cs.PF': '#F57C00',
  'cs.PL': '#7B1FA2',
  'cs.RO': '#D32F2F',
  'cs.SC': '#00796B',
  'cs.SD': '#303F9F',
  'cs.SE': '#E64A19',
  'cs.CC': '#8BC34A',
  'cs.CE': '#FF5722',
  'cs.CG': '#03A9F4',
  'cs.GT': '#CDDC39',
  'cs.CY': '#A1887F',
  'cs.DM': '#90A4AE',
  'cs.MA': '#B2EB2B',
  'cs.NA': '#FF8A65',
  'cs.SI': '#BA68C8',
  'cs.SY': '#4DD0E1',
}

// Quantitative Finance categories
export const QFIN_CATEGORY_IDS: string[] = [
  'q-fin.CP', 'q-fin.EC', 'q-fin.GN', 'q-fin.MF', 'q-fin.PM',
  'q-fin.PR', 'q-fin.RM', 'q-fin.ST', 'q-fin.TR'
]

export const qfinCategories: Category[] = [
  { id: 'q-fin*', name: 'All Quantitative Finance' },
  { id: 'q-fin.CP', name: 'Computational Finance' },
  { id: 'q-fin.EC', name: 'Economics' },
  { id: 'q-fin.GN', name: 'General Finance' },
  { id: 'q-fin.MF', name: 'Mathematical Finance' },
  { id: 'q-fin.PM', name: 'Portfolio Management' },
  { id: 'q-fin.PR', name: 'Pricing of Securities' },
  { id: 'q-fin.RM', name: 'Risk Management' },
  { id: 'q-fin.ST', name: 'Statistical Finance' },
  { id: 'q-fin.TR', name: 'Trading and Market Microstructure' },
]

export const qfinCategoryColors: Record<string, string> = {
  'q-fin.CP': '#1976D2',
  'q-fin.EC': '#0da5e0ff',
  'q-fin.GN': '#388E3C',
  'q-fin.MF': '#F57C00',
  'q-fin.PM': '#7B1FA2',
  'q-fin.PR': '#D32F2F',
  'q-fin.RM': '#C2185B',
  'q-fin.ST': '#00796B',
  'q-fin.TR': '#5D4037',
}

// Statistics categories
export const STAT_CATEGORY_IDS: string[] = [
  'stat.AP', 'stat.CO', 'stat.ME', 'stat.ML', 'stat.OT', 'stat.TH'
]

export const statCategories: Category[] = [
  { id: 'stat*', name: 'All Statistics' },
  { id: 'stat.AP', name: 'Applications' },
  { id: 'stat.CO', name: 'Computation' },
  { id: 'stat.ME', name: 'Methodology' },
  { id: 'stat.ML', name: 'Machine Learning' },
  { id: 'stat.OT', name: 'Other Statistics' },
  { id: 'stat.TH', name: 'Statistics Theory' },
]

export const statCategoryColors: Record<string, string> = {
  'stat.AP': '#00ACC1',
  'stat.CO': '#8BC34A',
  'stat.ME': '#FFA726',
  'stat.ML': '#9C27B0',
  'stat.OT': '#78909C',
  'stat.TH': '#5C6BC0',
}

// Economics categories
export const ECON_CATEGORY_IDS: string[] = [
  'econ.EM', 'econ.GN', 'econ.TH'
]

export const econCategories: Category[] = [
  { id: 'econ*', name: 'All Economics' },
  { id: 'econ.EM', name: 'Econometrics' },
  { id: 'econ.GN', name: 'General Economics' },
  { id: 'econ.TH', name: 'Theoretical Economics' },
]

export const econCategoryColors: Record<string, string> = {
  'econ.EM': '#E91E63',
  'econ.GN': '#3F51B5',
  'econ.TH': '#673AB7',
}

// Quantitative Biology categories
export const QBIO_CATEGORY_IDS: string[] = [
  'q-bio.BM', 'q-bio.CB', 'q-bio.GN', 'q-bio.MN', 'q-bio.NC',
  'q-bio.OT', 'q-bio.PE', 'q-bio.QM', 'q-bio.SC', 'q-bio.TO'
]

export const qbioCategories: Category[] = [
  { id: 'q-bio*', name: 'All Quantitative Biology' },
  { id: 'q-bio.BM', name: 'Biomolecules' },
  { id: 'q-bio.CB', name: 'Cell Behavior' },
  { id: 'q-bio.GN', name: 'Genomics' },
  { id: 'q-bio.MN', name: 'Molecular Networks' },
  { id: 'q-bio.NC', name: 'Neurons and Cognition' },
  { id: 'q-bio.OT', name: 'Other Quantitative Biology' },
  { id: 'q-bio.PE', name: 'Populations and Evolution' },
  { id: 'q-bio.QM', name: 'Quantitative Methods' },
  { id: 'q-bio.SC', name: 'Subcellular Processes' },
  { id: 'q-bio.TO', name: 'Tissues and Organs' },
]

export const qbioCategoryColors: Record<string, string> = {
  'q-bio.BM': '#4CAF50',
  'q-bio.CB': '#8BC34A',
  'q-bio.GN': '#CDDC39',
  'q-bio.MN': '#FFEB3B',
  'q-bio.NC': '#FFC107',
  'q-bio.OT': '#78909C',
  'q-bio.PE': '#FF9800',
  'q-bio.QM': '#FF5722',
  'q-bio.SC': '#795548',
  'q-bio.TO': '#607D8B',
}

// Subject group configuration
export const CATEGORY_GROUPS: CategoryGroup[] = [
  {
    id: 'cs',
    name: 'Computer Science',
    wildcard: 'cs*',
    categories: categories.filter(cat => cat.id !== 'cs*'),
    colors: categoryColors,
    color: '#FFC107'
  },
  {
    id: 'q-fin',
    name: 'Quantitative Finance',
    wildcard: 'q-fin*',
    categories: qfinCategories.filter(cat => cat.id !== 'q-fin*'),
    colors: qfinCategoryColors,
    color: '#1976D2'
  },
  {
    id: 'stat',
    name: 'Statistics',
    wildcard: 'stat*',
    categories: statCategories.filter(cat => cat.id !== 'stat*'),
    colors: statCategoryColors,
    color: '#00ACC1'
  },
  {
    id: 'econ',
    name: 'Economics',
    wildcard: 'econ*',
    categories: econCategories.filter(cat => cat.id !== 'econ*'),
    colors: econCategoryColors,
    color: '#E91E63'
  },
  {
    id: 'q-bio',
    name: 'Quantitative Biology',
    wildcard: 'q-bio*',
    categories: qbioCategories.filter(cat => cat.id !== 'q-bio*'),
    colors: qbioCategoryColors,
    color: '#4CAF50'
  }
]

// All categories merged
export const ALL_CATEGORIES: Category[] = [
  ...categories,
  ...qfinCategories,
  ...statCategories,
  ...econCategories,
  ...qbioCategories,
]

export const ALL_CATEGORY_COLORS: Record<string, string> = {
  ...categoryColors,
  ...qfinCategoryColors,
  ...statCategoryColors,
  ...econCategoryColors,
  ...qbioCategoryColors,
}

// Get subject group color (for root nodes)
export const GROUP_COLORS: Record<string, string> = {
  'cs*': '#FFC107',
  'q-fin*': '#1976D2',
  'stat*': '#00ACC1',
  'econ*': '#E91E63',
  'q-bio*': '#4CAF50',
}

export const getCategoryColor = (category: string | null): string => {
  if (!category) return '#9E9E9E'
  
  // Check if it's a subject wildcard
  if (GROUP_COLORS[category]) return GROUP_COLORS[category]
  
  return ALL_CATEGORY_COLORS[category] || '#9E9E9E'
}

export const getTagStyle = (category: string, isMinimal: boolean = false): Record<string, string> => {
  if (isMinimal) {
    return {
      backgroundColor: 'var(--tag-category-bg)',
      color: 'var(--tag-category)',
      border: '1px solid var(--tag-category-border)'
    }
  }
  const color = getCategoryColor(category)
    return {
        backgroundColor: color + '15',
        color: color,
        border: `1px solid ${color}30`
    }
}

export const getCategoryFullName = (category: string): string => {
    if (!category) return 'Unknown Category'
    const categoryData = ALL_CATEGORIES.find(cat => cat.id === category)
    return categoryData?.name || category
}

export const getCategoryShortName = (category: string): string => {
    if (!category) return 'CS'
    // Handle wildcard
    if (category.endsWith('*')) {
      return category.replace('*', '').toUpperCase()
    }
    const parts = category.split('.')
    return parts[parts.length - 1]?.toUpperCase() || category.toUpperCase()
}

// Get subject group
export const getCategoryGroup = (category: string): CategoryGroup | undefined => {
  // Handle wildcard
  if (category.endsWith('*')) {
    const groupId = category.replace('*', '')
    return CATEGORY_GROUPS.find(g => g.id === groupId)
  }
  // Handle specific category
  const prefix = category.split('.')[0]
  return CATEGORY_GROUPS.find(g => g.id === prefix)
}

// Check if category belongs to known subject
export const isKnownCategory = (category: string): boolean => {
  if (category.endsWith('*')) {
    return CATEGORY_GROUPS.some(g => g.wildcard === category)
  }
  return ALL_CATEGORIES.some(cat => cat.id === category)
}
