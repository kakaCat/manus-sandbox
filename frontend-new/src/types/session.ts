export interface Session {
  session_id: string
  sandbox_id: string
  title: string
  status: string
  created_at: string
  updated_at: string
  events: Event[]
  unread_message_count: number
}

export interface Event {
  event_type: string
  step?: string
  message?: string
}

export interface ChatRequest {
  message: string
  timestamp?: number
}

export interface CreateSessionResponse {
  session_id: string
  sandbox_id: string
}

export interface ListSessionsResponse {
  sessions: Session[]
}
