export type MatchItem = {
  id: string
  label: string
  kind: string
  score: number
  details?: string | null
}

export type ChatResponse = {
  intent: string
  confidence: string
  answer: string
  matches: MatchItem[]
  suggested_queries: string[]
}

export type Faculty = {
  id: string
  name: string
  short_name?: string | null
  campus?: string | null
  description?: string | null
}

export type Department = {
  id: string
  faculty_id?: string | null
  name: string
  aliases: string[]
  campus?: string | null
  location_guide?: string | null
  notes?: string | null
}

export type StaffMember = {
  id: string
  full_name: string
  title?: string | null
  rank_role?: string | null
  faculty_id?: string | null
  department_id?: string | null
  campus?: string | null
  specializations: string[]
  bio?: string | null
  aliases: string[]
  source_section?: string | null
  source_notes?: string | null
  is_active: boolean
}

export type LocationGuide = {
  id: string
  faculty_id?: string | null
  department_id?: string | null
  campus?: string | null
  directions_text: string
}

export type AuthUser = {
  id: number
  full_name: string
  email: string
  role: 'super_admin' | 'editor' | 'viewer'
  is_active: boolean
}
