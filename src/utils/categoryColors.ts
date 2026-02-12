export interface Category {
  id: string
  name: string
}

export const categories: Category[] = [
  { id: 'cs*', name: 'All Computer Science' },
  { id: 'cs.AI', name: 'Artificial Intelligence' },
  { id: 'cs.AR', name: 'Hardware Architecture' },
  { id: 'cs.CL', name: 'Computation and Language' },
  { id: 'cs.CC', name: 'Computational Complexity' },
  { id: 'cs.CE', name: 'Computational Engineering, Finance, and Science' },
  { id: 'cs.CG', name: 'Computational Geometry' },
  { id: 'cs.GT', name: 'Computer Science and Game Theory' },
  { id: 'cs.CV', name: 'Computer Vision and Pattern Recognition' },
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
  { id: 'cs.LG', name: 'Machine Learning' },
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
  { id: 'cs.SY', name: 'Systems and Control' }
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
  'cs.SY': '#4DD0E1'
}

export const getCategoryColor = (category: string): string => {
  return categoryColors[category] || '#9E9E9E'
}

export const getTagStyle = (category: string): Record<string, string> => {
  const color = getCategoryColor(category)
  return {
    backgroundColor: color + '15',
    color: color,
    border: `1px solid ${color}30`
  }
}

export const getCategoryFullName = (category: string): string => {
  if (!category) return 'Unknown Category'
  const categoryData = categories.find(cat => cat.id === category)
  return categoryData?.name || category
}

export const getCategoryShortName = (category: string): string => {
  if (!category) return 'CS'
  const parts = category.split('.')
  return parts[parts.length - 1]?.toUpperCase() || category.toUpperCase()
}
