import type {
  AuthUser,
  ChatResponse,
  Department,
  Faculty,
  LocationGuide,
  StaffMember,
} from '../types'

type RequestOptions = Omit<RequestInit, 'body'> & {
  json?: unknown
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(path, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    body: options.json === undefined ? undefined : JSON.stringify(options.json),
  })

  if (response.status === 204) {
    return undefined as T
  }

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = typeof payload?.detail === 'string' ? payload.detail : 'Request failed'
    throw new ApiError(detail, response.status)
  }
  return payload as T
}

export const api = {
  queryChat: (query: string) =>
    request<ChatResponse>('/api/chat/query', {
      method: 'POST',
      json: { query },
    }),
  listStaff: () => request<StaffMember[]>('/api/staff'),
  listDepartments: () => request<Department[]>('/api/departments'),
  listFaculties: () => request<Faculty[]>('/api/faculties'),
  listLocationGuides: () => request<LocationGuide[]>('/api/location-guides'),
  login: (email: string, password: string) =>
    request<{ user: AuthUser }>('/api/auth/login', {
      method: 'POST',
      json: { email, password },
    }),
  logout: () => request<{ message: string }>('/api/auth/logout', { method: 'POST' }),
  me: () => request<AuthUser>('/api/auth/me'),
  listUsers: () => request<AuthUser[]>('/api/admin/users'),
  createFaculty: (payload: Faculty) => request<Faculty>('/api/faculties', { method: 'POST', json: payload }),
  updateFaculty: (id: string, payload: Partial<Faculty>) =>
    request<Faculty>(`/api/faculties/${id}`, { method: 'PATCH', json: payload }),
  deleteFaculty: (id: string) => request<{ message: string }>(`/api/faculties/${id}`, { method: 'DELETE' }),
  createDepartment: (payload: Department) =>
    request<Department>('/api/departments', { method: 'POST', json: payload }),
  updateDepartment: (id: string, payload: Partial<Department>) =>
    request<Department>(`/api/departments/${id}`, { method: 'PATCH', json: payload }),
  deleteDepartment: (id: string) =>
    request<{ message: string }>(`/api/departments/${id}`, { method: 'DELETE' }),
  createStaff: (payload: StaffMember) => request<StaffMember>('/api/staff', { method: 'POST', json: payload }),
  updateStaff: (id: string, payload: Partial<StaffMember>) =>
    request<StaffMember>(`/api/staff/${id}`, { method: 'PATCH', json: payload }),
  deleteStaff: (id: string) => request<{ message: string }>(`/api/staff/${id}`, { method: 'DELETE' }),
  createLocationGuide: (payload: LocationGuide) =>
    request<LocationGuide>('/api/location-guides', { method: 'POST', json: payload }),
  updateLocationGuide: (id: string, payload: Partial<LocationGuide>) =>
    request<LocationGuide>(`/api/location-guides/${id}`, { method: 'PATCH', json: payload }),
  deleteLocationGuide: (id: string) =>
    request<{ message: string }>(`/api/location-guides/${id}`, { method: 'DELETE' }),
  createUser: (payload: { full_name: string; email: string; role: string; is_active: boolean; password: string }) =>
    request<AuthUser>('/api/admin/users', { method: 'POST', json: payload }),
  updateUser: (
    id: number,
    payload: Partial<{ full_name: string; email: string; role: string; is_active: boolean; password: string }>,
  ) => request<AuthUser>(`/api/admin/users/${id}`, { method: 'PATCH', json: payload }),
  deleteUser: (id: number) => request<{ message: string }>(`/api/admin/users/${id}`, { method: 'DELETE' }),
}
