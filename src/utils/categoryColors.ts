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
  icon: string  // SVG path for subject icon
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

// Electrical Engineering and Systems Science categories
export const EESS_CATEGORY_IDS: string[] = [
  'eess.AS', 'eess.IV', 'eess.SP', 'eess.SY'
]

export const eessCategories: Category[] = [
  { id: 'eess*', name: 'All Electrical Engineering and Systems Science' },
  { id: 'eess.AS', name: 'Audio and Speech Processing' },
  { id: 'eess.IV', name: 'Image and Video Processing' },
  { id: 'eess.SP', name: 'Signal Processing' },
  { id: 'eess.SY', name: 'Systems and Control' },
]

export const eessCategoryColors: Record<string, string> = {
  'eess.AS': '#9C27B0',
  'eess.IV': '#E91E63',
  'eess.SP': '#00BCD4',
  'eess.SY': '#3F51B5',
}

// Mathematics categories
export const MATH_CATEGORY_IDS: string[] = [
  'math.AC', 'math.AG', 'math.AP', 'math.AT', 'math.CA', 'math.CO', 'math.CT',
  'math.CV', 'math.DG', 'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GR',
  'math.GT', 'math.HO', 'math.IT', 'math.KT', 'math.LO', 'math.MG', 'math.MP',
  'math.NA', 'math.NT', 'math.OA', 'math.OC', 'math.PR', 'math.QA', 'math.RA',
  'math.RT', 'math.SG', 'math.SP', 'math.ST'
]

export const mathCategories: Category[] = [
  { id: 'math*', name: 'All Mathematics' },
  { id: 'math.AC', name: 'Commutative Algebra' },
  { id: 'math.AG', name: 'Algebraic Geometry' },
  { id: 'math.AP', name: 'Analysis of PDEs' },
  { id: 'math.AT', name: 'Algebraic Topology' },
  { id: 'math.CA', name: 'Classical Analysis and ODEs' },
  { id: 'math.CO', name: 'Combinatorics' },
  { id: 'math.CT', name: 'Category Theory' },
  { id: 'math.CV', name: 'Complex Variables' },
  { id: 'math.DG', name: 'Differential Geometry' },
  { id: 'math.DS', name: 'Dynamical Systems' },
  { id: 'math.FA', name: 'Functional Analysis' },
  { id: 'math.GM', name: 'General Mathematics' },
  { id: 'math.GN', name: 'General Topology' },
  { id: 'math.GR', name: 'Group Theory' },
  { id: 'math.GT', name: 'Geometric Topology' },
  { id: 'math.HO', name: 'History and Overview' },
  { id: 'math.IT', name: 'Information Theory' },
  { id: 'math.KT', name: 'K-Theory and Homology' },
  { id: 'math.LO', name: 'Logic' },
  { id: 'math.MG', name: 'Metric Geometry' },
  { id: 'math.MP', name: 'Mathematical Physics' },
  { id: 'math.NA', name: 'Numerical Analysis' },
  { id: 'math.NT', name: 'Number Theory' },
  { id: 'math.OA', name: 'Operator Algebras' },
  { id: 'math.OC', name: 'Optimization and Control' },
  { id: 'math.PR', name: 'Probability' },
  { id: 'math.QA', name: 'Quantum Algebra' },
  { id: 'math.RA', name: 'Rings and Algebras' },
  { id: 'math.RT', name: 'Representation Theory' },
  { id: 'math.SG', name: 'Symplectic Geometry' },
  { id: 'math.SP', name: 'Spectral Theory' },
  { id: 'math.ST', name: 'Statistics Theory' },
]

export const mathCategoryColors: Record<string, string> = {
  'math.AC': '#E91E63',
  'math.AG': '#9C27B0',
  'math.AP': '#673AB7',
  'math.AT': '#3F51B5',
  'math.CA': '#2196F3',
  'math.CO': '#03A9F4',
  'math.CT': '#00BCD4',
  'math.CV': '#009688',
  'math.DG': '#4CAF50',
  'math.DS': '#8BC34A',
  'math.FA': '#CDDC39',
  'math.GM': '#FFEB3B',
  'math.GN': '#FFC107',
  'math.GR': '#FF9800',
  'math.GT': '#FF5722',
  'math.HO': '#795548',
  'math.IT': '#607D8B',
  'math.KT': '#E91E63',
  'math.LO': '#9C27B0',
  'math.MG': '#673AB7',
  'math.MP': '#3F51B5',
  'math.NA': '#2196F3',
  'math.NT': '#03A9F4',
  'math.OA': '#00BCD4',
  'math.OC': '#009688',
  'math.PR': '#4CAF50',
  'math.QA': '#8BC34A',
  'math.RA': '#CDDC39',
  'math.RT': '#FFEB3B',
  'math.SG': '#FFC107',
  'math.SP': '#FF9800',
  'math.ST': '#FF5722',
}

// Physics categories (physics.* only)
export const PHYSICS_CATEGORY_IDS: string[] = [
  'physics.acc-ph', 'physics.ao-ph', 'physics.app-ph', 'physics.atm-clus',
  'physics.atom-ph', 'physics.bio-ph', 'physics.chem-ph', 'physics.class-ph',
  'physics.comp-ph', 'physics.data-an', 'physics.ed-ph', 'physics.flu-dyn',
  'physics.gen-ph', 'physics.geo-ph', 'physics.hist-ph', 'physics.ins-det',
  'physics.med-ph', 'physics.optics', 'physics.plasm-ph', 'physics.pop-ph',
  'physics.soc-ph', 'physics.space-ph'
]

export const physicsCategories: Category[] = [
  { id: 'physics*', name: 'All Physics' },
  { id: 'physics.acc-ph', name: 'Accelerator Physics' },
  { id: 'physics.ao-ph', name: 'Atmospheric and Oceanic Physics' },
  { id: 'physics.app-ph', name: 'Applied Physics' },
  { id: 'physics.atm-clus', name: 'Atomic and Molecular Clusters' },
  { id: 'physics.atom-ph', name: 'Atomic Physics' },
  { id: 'physics.bio-ph', name: 'Biological Physics' },
  { id: 'physics.chem-ph', name: 'Chemical Physics' },
  { id: 'physics.class-ph', name: 'Classical Physics' },
  { id: 'physics.comp-ph', name: 'Computational Physics' },
  { id: 'physics.data-an', name: 'Data Analysis, Statistics and Probability' },
  { id: 'physics.ed-ph', name: 'Physics Education' },
  { id: 'physics.flu-dyn', name: 'Fluid Dynamics' },
  { id: 'physics.gen-ph', name: 'General Physics' },
  { id: 'physics.geo-ph', name: 'Geophysics' },
  { id: 'physics.hist-ph', name: 'History and Philosophy of Physics' },
  { id: 'physics.ins-det', name: 'Instrumentation and Detectors' },
  { id: 'physics.med-ph', name: 'Medical Physics' },
  { id: 'physics.optics', name: 'Optics' },
  { id: 'physics.plasm-ph', name: 'Plasma Physics' },
  { id: 'physics.pop-ph', name: 'Popular Physics' },
  { id: 'physics.soc-ph', name: 'Physics and Society' },
  { id: 'physics.space-ph', name: 'Space Physics' },
]

export const physicsCategoryColors: Record<string, string> = {
  'physics.acc-ph': '#E91E63',
  'physics.ao-ph': '#9C27B0',
  'physics.app-ph': '#673AB7',
  'physics.atm-clus': '#3F51B5',
  'physics.atom-ph': '#2196F3',
  'physics.bio-ph': '#03A9F4',
  'physics.chem-ph': '#00BCD4',
  'physics.class-ph': '#009688',
  'physics.comp-ph': '#4CAF50',
  'physics.data-an': '#8BC34A',
  'physics.ed-ph': '#CDDC39',
  'physics.flu-dyn': '#FFEB3B',
  'physics.gen-ph': '#FFC107',
  'physics.geo-ph': '#FF9800',
  'physics.hist-ph': '#FF5722',
  'physics.ins-det': '#795548',
  'physics.med-ph': '#607D8B',
  'physics.optics': '#E91E63',
  'physics.plasm-ph': '#9C27B0',
  'physics.pop-ph': '#673AB7',
  'physics.soc-ph': '#3F51B5',
  'physics.space-ph': '#2196F3',
}

// Subject group configuration
export const CATEGORY_GROUPS: CategoryGroup[] = [
  {
    id: 'cs',
    name: 'Computer Science',
    wildcard: 'cs*',
    categories: categories.filter(cat => cat.id !== 'cs*'),
    colors: categoryColors,
    color: '#2196F3',
    // Computer monitor icon (hollow style)
    icon: 'M4 6h16v10H4zM6 4h12c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H6c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zM8 20h8M12 16v4'
  },
  {
    id: 'q-fin',
    name: 'Quantitative Finance',
    wildcard: 'q-fin*',
    categories: qfinCategories.filter(cat => cat.id !== 'q-fin*'),
    colors: qfinCategoryColors,
    color: '#7f0aadff',
    // Stock chart trend line (hollow style)
    icon: 'M3 3v18h18M7 14l3-4 3 2 4-6'
  },
  {
    id: 'stat',
    name: 'Statistics',
    wildcard: 'stat*',
    categories: statCategories.filter(cat => cat.id !== 'stat*'),
    colors: statCategoryColors,
    color: '#00ACC1',
    // Bell curve / normal distribution (hollow style)
    icon: 'M3 17h18M5 17c0-8 3-13 7-13s7 5 7 13'
  },
  {
    id: 'econ',
    name: 'Economics',
    wildcard: 'econ*',
    categories: econCategories.filter(cat => cat.id !== 'econ*'),
    colors: econCategoryColors,
    color: '#E91E63',
    // Dollar sign (hollow style)
    icon: 'M12 1v22M8 6h8c1.1 0 2 .9 2 2s-.9 2-2 2H8c-1.1 0-2-.9-2-2s.9-2 2-2zM8 14h10c1.1 0 2 .9 2 2s-.9 2-2 2H8c-1.1 0-2-.9-2-2s.9-2 2-2z'
  },
  {
    id: 'q-bio',
    name: 'Quantitative Biology',
    wildcard: 'q-bio*',
    categories: qbioCategories.filter(cat => cat.id !== 'q-bio*'),
    colors: qbioCategoryColors,
    color: '#4CAF50',
    // DNA helix (hollow style)
    icon: 'M4 4c2 0 4 2 4 4s-2 4-4 4M12 4c2 0 4 2 4 4s-2 4-4 4M4 12c2 0 4 2 4 4s-2 4-4 4M12 12c2 0 4 2 4 4s-2 4-4 4M8 8h8M8 16h8'
  },
  {
    id: 'eess',
    name: 'Electrical Engineering and Systems Science',
    wildcard: 'eess*',
    categories: eessCategories.filter(cat => cat.id !== 'eess*'),
    colors: eessCategoryColors,
    color: '#9C27B0',
    // Circuit chip (hollow style)
    icon: 'M6 6h12v12H6zM6 6l-4 0M6 12l-4 0M6 18l-4 0M18 6l4 0M18 12l4 0M18 18l4 0M6 6l0-4M12 6l0-4M18 6l0-4M6 18l0 4M12 18l0 4M18 18l0 4'
  },
  {
    id: 'math',
    name: 'Mathematics',
    wildcard: 'math*',
    categories: mathCategories.filter(cat => cat.id !== 'math*'),
    colors: mathCategoryColors,
    color: '#E91E63',
    // Integral symbol (hollow style)
    icon: 'M4 4c0 3 1 5 2 8s2 5 2 8M20 4c0 3-1 5-2 8s-2 5-2 8M8 8h8M8 16h8'
  },
  {
    id: 'physics',
    name: 'Physics',
    wildcard: 'physics*',
    categories: physicsCategories.filter(cat => cat.id !== 'physics*'),
    colors: physicsCategoryColors,
    color: '#1976D2',
    // Atom with orbits (hollow style)
    icon: 'M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0M12 2c5 5 5 17 0 22M12 2c-5 5-5 17 0 22M2 12c5-5 17-5 22 0M2 12c5 5 17 5 22 0'
  }
]

// All categories merged
export const ALL_CATEGORIES: Category[] = [
  ...categories,
  ...qfinCategories,
  ...statCategories,
  ...econCategories,
  ...qbioCategories,
  ...eessCategories,
  ...mathCategories,
  ...physicsCategories,
]

export const ALL_CATEGORY_COLORS: Record<string, string> = {
  ...categoryColors,
  ...qfinCategoryColors,
  ...statCategoryColors,
  ...econCategoryColors,
  ...qbioCategoryColors,
  ...eessCategoryColors,
  ...mathCategoryColors,
  ...physicsCategoryColors,
}

// Get subject group color (for root nodes)
export const GROUP_COLORS: Record<string, string> = {
  'cs*': '#FFC107',
  'q-fin*': '#1976D2',
  'stat*': '#00ACC1',
  'econ*': '#E91E63',
  'q-bio*': '#4CAF50',
  'eess*': '#9C27B0',
  'math*': '#E91E63',
  'physics*': '#2196F3',
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
