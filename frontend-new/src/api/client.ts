import axios from 'axios'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { Session, CreateSessionResponse, ListSessionsResponse, ChatRequest, Event } from '@/types/session'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000
})

export const api = {
  async createSession(user_id: string = 'anonymous'): Promise<CreateSessionResponse> {
    const response = await apiClient.put<CreateSessionResponse>('/sessions', null, {
      params: { user_id }
    })
    return response.data
  },

  async listSessions(user_id: string = 'anonymous'): Promise<ListSessionsResponse> {
    const response = await apiClient.get<ListSessionsResponse>('/sessions', {
      params: { user_id }
    })
    return response.data
  },

  async getSession(session_id: string, user_id: string = 'anonymous'): Promise<Session> {
    const response = await apiClient.get<Session>(`/sessions/${session_id}`, {
      params: { user_id }
    })
    return response.data
  },

  async deleteSession(session_id: string, user_id: string = 'anonymous'): Promise<void> {
    await apiClient.delete(`/sessions/${session_id}`, {
      params: { user_id }
    })
  },

  async stopSession(session_id: string, user_id: string = 'anonymous'): Promise<void> {
    await apiClient.post(`/sessions/${session_id}/stop`, null, {
      params: { user_id }
    })
  },

  chat(
    session_id: string,
    request: ChatRequest,
    user_id: string = 'anonymous',
    onEvent: (event: Event) => void,
    onError?: (error: Error) => void
  ): () => void {
    const controller = new AbortController()
    const url = `${API_BASE}/sessions/${session_id}/chat?user_id=${user_id}`

    fetchEventSource(url, {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        'Content-Type': 'application/json'
      },
      signal: controller.signal,

      onmessage(event) {
        if (event.data) {
          const data = JSON.parse(event.data)
          onEvent(data)
        }
      },

      onerror(error) {
        console.error('SSE Error:', error)
        onError?.(error)
        controller.abort()
      },

      onclose() {
        console.log('SSE Connection closed')
      }
    })

    return () => controller.abort()
  }
}
