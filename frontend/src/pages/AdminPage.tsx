import type { ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { ActionRow, emptyDepartment, emptyFaculty, emptyLocation, emptyStaff, emptyUser, labelName, RecordList, type UserDraft } from '../components/forms'
import { DepartmentForm, FacultyForm, LocationForm, StaffForm, UserForm } from '../components/AdminForms'
import { ApiError, api } from '../lib/api'
import type { AuthUser, Department, Faculty, LocationGuide, StaffMember } from '../types'

type AdminTab = 'staff' | 'departments' | 'faculties' | 'locations' | 'users'

export function AdminPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<AdminTab>('staff')
  const [loginForm, setLoginForm] = useState({ email: 'admin@umat.edu.gh', password: 'Admin123!' })
  const meQuery = useQuery({ queryKey: ['me'], queryFn: api.me, retry: false })
  const loginMutation = useMutation({
    mutationFn: () => api.login(loginForm.email, loginForm.password),
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })
  const logoutMutation = useMutation({
    mutationFn: api.logout,
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })

  if (!meQuery.data) {
    return (
      <section className="panel panel--login" style={{ maxWidth: '440px', margin: '10vh auto', textAlign: 'center' }}>
        <div className="panel__header">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto 1rem', display: 'block' }}>
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <h2 style={{ fontSize: '1.75rem' }}>Admin Sign In</h2>
          <p className="muted">Use the seeded accounts or any users created later from this console.</p>
        </div>
        <form
          className="stack"
          style={{ marginTop: '1.5rem' }}
          onSubmit={(event) => {
            event.preventDefault()
            loginMutation.mutate()
          }}
        >
          <input className="input" value={loginForm.email} onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))} placeholder="Email" />
          <input className="input" type="password" value={loginForm.password} onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))} placeholder="Password" />
          <button className="button button--primary" type="submit" disabled={loginMutation.isPending} style={{ marginTop: '0.5rem', padding: '1rem', fontSize: '1.05rem' }}>
            {loginMutation.isPending ? 'Authenticating…' : 'Sign In'}
          </button>
          {loginMutation.isError ? <p className="status status--error">{(loginMutation.error as ApiError).message}</p> : null}
        </form>
      </section>
    )
  }

  return (
    <>
      <section className="panel panel--toolbar" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', padding: '1.5rem 2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', marginBottom: '0.2rem' }}>{meQuery.data.full_name}</h2>
          <p className="muted" style={{ fontSize: '0.9rem' }}>
            Signed in as <strong style={{ color: 'var(--ink)' }}>{meQuery.data.role.replace('_', ' ')}</strong>
          </p>
        </div>
        <button className="button" type="button" onClick={() => logoutMutation.mutate()} disabled={logoutMutation.isPending}>
          {logoutMutation.isPending ? 'Signing out…' : 'Sign Out'}
        </button>
      </section>
      <DashboardBody tab={tab} setTab={setTab} user={meQuery.data} />
    </>
  )
}

function DashboardBody({ tab, setTab, user }: { tab: AdminTab; setTab: (tab: AdminTab) => void; user: AuthUser }) {
  const { data: staff = [] } = useQuery({ queryKey: ['staff'], queryFn: api.listStaff })
  const { data: departments = [] } = useQuery({ queryKey: ['departments'], queryFn: api.listDepartments })
  const { data: faculties = [] } = useQuery({ queryKey: ['faculties'], queryFn: api.listFaculties })
  const { data: locationGuides = [] } = useQuery({ queryKey: ['locationGuides'], queryFn: api.listLocationGuides })
  const usersQuery = useQuery({ queryKey: ['users'], queryFn: api.listUsers, enabled: user.role === 'super_admin', retry: false })
  const tabs: AdminTab[] = user.role === 'super_admin' ? ['staff', 'departments', 'faculties', 'locations', 'users'] : ['staff', 'departments', 'faculties', 'locations']

  return (
    <section className="panel" style={{ paddingTop: '1.5rem' }}>
      <div className="tabs" style={{ marginBottom: '2rem' }}>
        {tabs.map((item) => (
          <button key={item} className={`tab ${tab === item ? 'tab--active' : ''}`} type="button" onClick={() => setTab(item)}>
            {item.charAt(0).toUpperCase() + item.slice(1)}
          </button>
        ))}
      </div>
      {tab === 'staff' ? <StaffManager staff={staff} departments={departments} faculties={faculties} user={user} /> : null}
      {tab === 'departments' ? <DepartmentManager departments={departments} faculties={faculties} user={user} /> : null}
      {tab === 'faculties' ? <FacultyManager faculties={faculties} user={user} /> : null}
      {tab === 'locations' ? <LocationManager locationGuides={locationGuides} faculties={faculties} departments={departments} user={user} /> : null}
      {tab === 'users' && user.role === 'super_admin' ? <UserManager users={usersQuery.data ?? []} /> : null}
    </section>
  )
}

function CrudShell({ title, description, error, children }: { title: string; description: string; error: unknown; children: ReactNode }) {
  return (
    <div className="crud">
      <div className="panel__header" style={{ marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.5rem' }}>{title}</h2>
        <p className="muted">{description}</p>
      </div>
      {error ? <p className="status status--error">{(error as ApiError).message}</p> : null}
      {children}
    </div>
  )
}

function FacultyManager({ faculties, user }: { faculties: Faculty[]; user: AuthUser }) {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState<Faculty>(emptyFaculty)
  const saveMutation = useMutation({ mutationFn: (payload: Faculty) => (faculties.some((item) => item.id === payload.id) ? api.updateFaculty(payload.id, payload) : api.createFaculty(payload)), onSuccess: async () => { setDraft(emptyFaculty); await queryClient.invalidateQueries({ queryKey: ['faculties'] }) } })
  const deleteMutation = useMutation({ mutationFn: api.deleteFaculty, onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['faculties'] }) })
  return (
    <CrudShell title="Faculties" description="Manage faculty metadata and campus context." error={saveMutation.error ?? deleteMutation.error}>
      <FacultyForm draft={draft} onChange={setDraft} disabled={user.role === 'viewer'} />
      <ActionRow canEdit={user.role !== 'viewer'} onSave={() => saveMutation.mutate(draft)} onReset={() => setDraft(emptyFaculty)} saveLabel={saveMutation.isPending ? 'Saving…' : 'Save Faculty'} />
      <RecordList items={faculties} renderItem={(faculty) => <div className="record__details"><strong style={{ fontSize: '1.1rem' }}>{faculty.name}</strong><span className="muted">{faculty.campus}</span></div>} onEdit={setDraft} onDelete={(faculty) => deleteMutation.mutate(faculty.id)} canDelete={user.role !== 'viewer'} />
    </CrudShell>
  )
}

function DepartmentManager({ departments, faculties, user }: { departments: Department[]; faculties: Faculty[]; user: AuthUser }) {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState<Department>(emptyDepartment)
  const saveMutation = useMutation({ mutationFn: (payload: Department) => (departments.some((item) => item.id === payload.id) ? api.updateDepartment(payload.id, payload) : api.createDepartment(payload)), onSuccess: async () => { setDraft(emptyDepartment); await queryClient.invalidateQueries({ queryKey: ['departments'] }) } })
  const deleteMutation = useMutation({ mutationFn: api.deleteDepartment, onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['departments'] }) })
  return (
    <CrudShell title="Departments" description="Keep aliases and location notes aligned with the registry." error={saveMutation.error ?? deleteMutation.error}>
      <DepartmentForm draft={draft} onChange={setDraft} faculties={faculties} disabled={user.role === 'viewer'} />
      <ActionRow canEdit={user.role !== 'viewer'} onSave={() => saveMutation.mutate(draft)} onReset={() => setDraft(emptyDepartment)} saveLabel={saveMutation.isPending ? 'Saving…' : 'Save Department'} />
      <RecordList items={departments} renderItem={(department) => <div className="record__details"><strong style={{ fontSize: '1.1rem' }}>{department.name}</strong><span className="muted">{department.campus}</span></div>} onEdit={setDraft} onDelete={(department) => deleteMutation.mutate(department.id)} canDelete={user.role !== 'viewer'} />
    </CrudShell>
  )
}

function StaffManager({ staff, departments, faculties, user }: { staff: StaffMember[]; departments: Department[]; faculties: Faculty[]; user: AuthUser }) {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState<StaffMember>(emptyStaff)
  const saveMutation = useMutation({ mutationFn: (payload: StaffMember) => (staff.some((item) => item.id === payload.id) ? api.updateStaff(payload.id, payload) : api.createStaff(payload)), onSuccess: async () => { setDraft(emptyStaff); await queryClient.invalidateQueries({ queryKey: ['staff'] }) } })
  const deleteMutation = useMutation({ mutationFn: api.deleteStaff, onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['staff'] }) })
  return (
    <CrudShell title="Staff Records" description="These records drive the chatbot and the public directory." error={saveMutation.error ?? deleteMutation.error}>
      <StaffForm draft={draft} onChange={setDraft} departments={departments} faculties={faculties} disabled={user.role === 'viewer'} />
      <ActionRow canEdit={user.role !== 'viewer'} onSave={() => saveMutation.mutate(draft)} onReset={() => setDraft(emptyStaff)} saveLabel={saveMutation.isPending ? 'Saving…' : 'Save Staff'} />
      <RecordList items={staff} renderItem={(member) => <div className="record__details"><strong style={{ fontSize: '1.1rem' }}>{labelName(member)}</strong><span className="muted">{member.rank_role}</span></div>} onEdit={setDraft} onDelete={(member) => deleteMutation.mutate(member.id)} canDelete={user.role !== 'viewer'} />
    </CrudShell>
  )
}

function LocationManager({ locationGuides, faculties, departments, user }: { locationGuides: LocationGuide[]; faculties: Faculty[]; departments: Department[]; user: AuthUser }) {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState<LocationGuide>(emptyLocation)
  const saveMutation = useMutation({ mutationFn: (payload: LocationGuide) => (locationGuides.some((item) => item.id === payload.id) ? api.updateLocationGuide(payload.id, payload) : api.createLocationGuide(payload)), onSuccess: async () => { setDraft(emptyLocation); await queryClient.invalidateQueries({ queryKey: ['locationGuides'] }) } })
  const deleteMutation = useMutation({ mutationFn: api.deleteLocationGuide, onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['locationGuides'] }) })
  return (
    <CrudShell title="Location Guides" description="Department-level guidance for office localization." error={saveMutation.error ?? deleteMutation.error}>
      <LocationForm draft={draft} onChange={setDraft} faculties={faculties} departments={departments} disabled={user.role === 'viewer'} />
      <ActionRow canEdit={user.role !== 'viewer'} onSave={() => saveMutation.mutate(draft)} onReset={() => setDraft(emptyLocation)} saveLabel={saveMutation.isPending ? 'Saving…' : 'Save Guide'} />
      <RecordList items={locationGuides} renderItem={(guide) => <div className="record__details"><strong style={{ fontSize: '1.1rem' }}>{guide.id}</strong><span className="muted">{guide.campus}</span></div>} onEdit={setDraft} onDelete={(guide) => deleteMutation.mutate(guide.id)} canDelete={user.role !== 'viewer'} />
    </CrudShell>
  )
}

function UserManager({ users }: { users: AuthUser[] }) {
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState<UserDraft>(emptyUser)
  const saveMutation = useMutation({ mutationFn: (payload: UserDraft) => (payload.id ? api.updateUser(payload.id, payload) : api.createUser(payload)), onSuccess: async () => { setDraft(emptyUser); await queryClient.invalidateQueries({ queryKey: ['users'] }) } })
  const deleteMutation = useMutation({ mutationFn: api.deleteUser, onSuccess: async () => queryClient.invalidateQueries({ queryKey: ['users'] }) })
  return (
    <CrudShell title="Admin Users" description="Super-admin only user management." error={saveMutation.error ?? deleteMutation.error}>
      <UserForm draft={draft} onChange={setDraft} disabled={saveMutation.isPending} />
      <ActionRow canEdit onSave={() => saveMutation.mutate(draft)} onReset={() => setDraft(emptyUser)} saveLabel={saveMutation.isPending ? 'Saving…' : 'Save User'} />
      <RecordList items={users} renderItem={(account) => <div className="record__details"><strong style={{ fontSize: '1.1rem' }}>{account.full_name}</strong><span className="muted">{account.role.replace('_', ' ')} · {account.email}</span></div>} onEdit={(account) => setDraft({ ...account, password: '', id: account.id })} onDelete={(account) => deleteMutation.mutate(account.id)} canDelete />
    </CrudShell>
  )
}
