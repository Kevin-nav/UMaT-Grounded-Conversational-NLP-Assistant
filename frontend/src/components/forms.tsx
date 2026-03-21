/* eslint-disable react-refresh/only-export-components */
import type { ReactNode } from 'react'

import type { AuthUser, Department, Faculty, LocationGuide, StaffMember } from '../types'

export type UserDraft = {
  id?: number
  full_name: string
  email: string
  role: AuthUser['role']
  is_active: boolean
  password: string
}

export const emptyFaculty: Faculty = {
  id: '',
  name: '',
  short_name: '',
  campus: '',
  description: '',
}

export const emptyDepartment: Department = {
  id: '',
  faculty_id: '',
  name: '',
  aliases: [],
  campus: '',
  location_guide: '',
  notes: '',
}

export const emptyStaff: StaffMember = {
  id: '',
  full_name: '',
  title: '',
  rank_role: '',
  faculty_id: '',
  department_id: '',
  campus: '',
  specializations: [],
  bio: '',
  aliases: [],
  source_section: '',
  source_notes: '',
  is_active: true,
}

export const emptyLocation: LocationGuide = {
  id: '',
  faculty_id: '',
  department_id: '',
  campus: '',
  directions_text: '',
}

export const emptyUser: UserDraft = {
  full_name: '',
  email: '',
  role: 'editor',
  is_active: true,
  password: '',
}

export function splitCsv(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function toCsv(values: string[]): string {
  return values.join(', ')
}

export function labelName(member: StaffMember): string {
  return member.title ? `${member.title} ${member.full_name}` : member.full_name
}

export function ActionRow({
  canEdit,
  onSave,
  onReset,
  saveLabel,
}: {
  canEdit: boolean
  onSave: () => void
  onReset: () => void
  saveLabel: string
}) {
  return (
    <div className="actions">
      <button className="button button--primary" type="button" onClick={onSave} disabled={!canEdit}>
        {saveLabel}
      </button>
      <button className="button" type="button" onClick={onReset}>
        Reset
      </button>
    </div>
  )
}

export function RecordList<T extends { id: string | number }>({
  items,
  renderItem,
  onEdit,
  onDelete,
  canDelete,
}: {
  items: T[]
  renderItem: (item: T) => ReactNode
  onEdit: (item: T) => void
  onDelete: (item: T) => void
  canDelete: boolean
}) {
  return (
    <div className="record-list">
      {items.map((item) => (
        <article key={item.id} className="record">
          <div className="record__content">{renderItem(item)}</div>
          <div className="record__actions" style={{ gap: '0.5rem' }}>
            <button className="chip" style={{ background: 'transparent', borderColor: 'var(--border)' }} type="button" onClick={() => onEdit(item)}>
              Edit
            </button>
            <button className="chip" style={{ background: 'transparent', borderColor: 'var(--border)' }} type="button" onClick={() => onDelete(item)} disabled={!canDelete}>
              Delete
            </button>
          </div>
        </article>
      ))}
    </div>
  )
}
