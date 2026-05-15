import http from './http'

const payloadEmpty = {}

export const authApi = {
  login: (payload: { username: string; password: string }) => http.post('/auth/login', payload),
  register: (payload: { username: string; password: string; display_name: string; email: string }) => http.post('/auth/register', payload),
  me: () => http.get('/auth/me'),
  searchUsers: (keyword = '') => http.get('/auth/users/search', { params: { keyword } }),
}

export const projectApi = {
  list: () => http.get('/projects'),
  create: (payload: Record<string, unknown>) => http.post('/projects', payload),
  detail: (id: string | number) => http.get(`/projects/${id}`),
  update: (id: string | number, payload: Record<string, unknown>) => http.put(`/projects/${id}`, payload),
  dashboard: (id: string | number) => http.get(`/projects/${id}/dashboard`),
  members: (id: string | number) => http.get(`/projects/${id}/members`),
  updateMember: (id: string | number, userId: number, payload: Record<string, unknown>) => http.put(`/projects/${id}/members/${userId}`, payload),
  removeMember: (id: string | number, userId: number) => http.delete(`/projects/${id}/members/${userId}`),
  invitations: (id: string | number) => http.get(`/projects/${id}/invitations`),
  sendInvitation: (id: string | number, payload: Record<string, unknown>) => http.post(`/projects/${id}/invitations`, payload),
  revokeInvitation: (id: number) => http.delete(`/projects/invitations/${id}`),
  myInvitations: () => http.get('/projects/me/invitations'),
  acceptInvitation: (id: number) => http.post(`/projects/invitations/${id}/accept`),
  rejectInvitation: (id: number) => http.post(`/projects/invitations/${id}/reject`),
  graph: (id: string | number) => http.get(`/projects/${id}/graph`),
  contribution: (id: string | number) => http.get(`/projects/${id}/contribution`),
  recalculateContribution: (id: string | number) => http.post(`/projects/${id}/contribution/recalculate`),
  riskAlerts: (id: string | number) => http.get(`/projects/${id}/risk-alerts`),
  scanRisk: (id: string | number) => http.post(`/projects/${id}/risk-alerts/scan`),
  resolveRisk: (id: number) => http.put(`/projects/risk-alerts/${id}/resolve`),
  git: (id: string | number) => http.get(`/projects/${id}/git/commits`),
  workspace: (id: string | number) => http.get(`/projects/${id}/workspace`),
}

export const taskApi = {
  list: (projectId: string | number) => http.get(`/projects/${projectId}/tasks`),
  myTasks: () => http.get('/me/tasks'),
  create: (projectId: string | number, payload: Record<string, unknown>) => http.post(`/projects/${projectId}/tasks`, payload),
  detail: (taskId: string | number) => http.get(`/tasks/${taskId}`),
  update: (taskId: string | number, payload: Record<string, unknown>) => http.put(`/tasks/${taskId}`, payload),
  remove: (taskId: string | number) => http.delete(`/tasks/${taskId}`),
  assign: (taskId: string | number, payload: Record<string, unknown>) => http.post(`/tasks/${taskId}/assign`, payload),
  accept: (taskId: string | number) => http.post(`/tasks/${taskId}/accept`),
  block: (taskId: string | number, payload: Record<string, unknown>) => http.post(`/tasks/${taskId}/block`, payload),
  complete: (taskId: string | number) => http.post(`/tasks/${taskId}/complete`, payloadEmpty),
  activities: (taskId: string | number) => http.get(`/tasks/${taskId}/activities`),
  conversation: (taskId: string | number) => http.get(`/tasks/${taskId}/conversation`),
  milestones: (projectId: string | number) => http.get(`/projects/${projectId}/milestones`),
  createMilestone: (projectId: string | number, payload: Record<string, unknown>) => http.post(`/projects/${projectId}/milestones`, payload),
}

export const conversationApi = {
  list: (projectId: string | number) => http.get(`/projects/${projectId}/conversations`),
  create: (projectId: string | number, payload: Record<string, unknown>) => http.post(`/projects/${projectId}/conversations`, payload),
  messages: (conversationId: string | number) => http.get(`/conversations/${conversationId}/messages`),
  sendMessage: (conversationId: string | number, payload: Record<string, unknown>) => http.post(`/conversations/${conversationId}/messages`, payload),
  read: (conversationId: string | number) => http.post(`/conversations/${conversationId}/read`),
}

export const documentApi = {
  list: (projectId: string | number) => http.get(`/projects/${projectId}/documents`),
  create: (projectId: string | number, payload: Record<string, unknown>) => http.post(`/projects/${projectId}/documents`, payload),
  detail: (id: string | number) => http.get(`/documents/${id}`),
  update: (id: string | number, payload: Record<string, unknown>) => http.put(`/documents/${id}`, payload),
  remove: (id: string | number) => http.delete(`/documents/${id}`),
  versions: (id: string | number) => http.get(`/documents/${id}/versions`),
  createVersion: (id: string | number, payload: Record<string, unknown>) => http.post(`/documents/${id}/versions`, payload),
}

export const fileApi = {
  list: (projectId: string | number) => http.get(`/projects/${projectId}/files`),
  upload: (projectId: string | number, payload: FormData) => http.post(`/projects/${projectId}/files/upload`, payload),
  remove: (id: string | number) => http.delete(`/files/${id}`),
}

export const notificationApi = {
  list: () => http.get('/notifications'),
  unreadCount: () => http.get('/notifications/unread-count'),
  markRead: (id: number) => http.post(`/notifications/${id}/read`),
  readAll: () => http.post('/notifications/read'),
}

export const aiApi = {
  planning: (payload: Record<string, unknown>) => http.post('/ai/planning', payload),
  confirm: (id: number) => http.post(`/ai/planning/${id}/confirm`),
  weeklyReport: (projectId: string | number) => http.post('/ai/reports/weekly', null, { params: { project_id: projectId } }),
}
