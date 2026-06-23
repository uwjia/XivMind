import { CATEGORY_GROUPS } from '@/utils/categoryColors'

// Supported subjects list
export const SUPPORTED_SUBJECTS = CATEGORY_GROUPS.map(g => g.id)

// Default subject
export const DEFAULT_SUBJECT = 'cs'

export const config = {
  maxResults: 50,
  defaultCategory: 'cs*',
  defaultSubject: DEFAULT_SUBJECT,
  defaultDateFilter: 'all',
  supportedSubjects: SUPPORTED_SUBJECTS,
}

// Get subject wildcard
export const getSubjectWildcard = (subject: string): string => {
  const group = CATEGORY_GROUPS.find(g => g.id === subject)
  return group?.wildcard || 'cs*'
}
