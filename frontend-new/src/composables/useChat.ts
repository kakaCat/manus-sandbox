import { ref, reactive } from 'vue'
import { api } from '@/api/client'
import type { Session, Event, ChatRequest } from '@/types/session'

export function useChat() {
  const currentSession = ref<Session | null>(null)
  const sessions = ref<Session[]>([])
  const messages = ref<Array<{ role: string; content: string }>>([])
  const events = ref<Event[]>([])
  const isLoading = ref(false)

  const activePanel = reactive({
    browser: false,
    shell: false,
    file: false,
    search: false
  })

  async function createSession() {
    try {
      const response = await api.createSession()
      currentSession.value = {
        ...response,
        title: 'New Session',
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        events: [],
        unread_message_count: 0
      }

      await loadSessions()
      return response.session_id
    } catch (error) {
      console.error('Failed to create session:', error)
      throw error
    }
  }

  async function loadSessions() {
    try {
      const response = await api.listSessions()
      sessions.value = response.sessions
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  async function selectSession(session_id: string) {
    try {
      currentSession.value = await api.getSession(session_id)
      messages.value = currentSession.value.events
        .filter(e => e.event_type === 'done')
        .map(e => ({
          role: 'assistant',
          content: e.message || ''
        }))
      events.value = currentSession.value.events
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  async function sendMessage(message: string) {
    if (!currentSession.value) {
      await createSession()
    }

    messages.value.push({ role: 'user', content: message })
    isLoading.value = true

    const request: ChatRequest = {
      message,
      timestamp: Date.now()
    }

    api.chat(
      currentSession.value!.session_id,
      request,
      undefined,
      (event: Event) => {
        events.value.push(event)

        if (event.event_type === 'step') {
          if (event.step === 'planner') {
            activePanel.search = true
          } else if (event.step === 'executor') {
            activePanel.shell = true
          }
        }

        if (event.event_type === 'done') {
          messages.value.push({ role: 'assistant', content: event.message || '' })
          isLoading.value = false
        }
      },
      (error) => {
        console.error('Chat error:', error)
        isLoading.value = false
      }
    )
  }

  async function stopSession() {
    if (!currentSession.value) return

    try {
      await api.stopSession(currentSession.value.session_id)
      currentSession.value.status = 'stopped'
    } catch (error) {
      console.error('Failed to stop session:', error)
    }
  }

  async function deleteSession(session_id: string) {
    try {
      await api.deleteSession(session_id)
      sessions.value = sessions.value.filter(s => s.session_id !== session_id)

      if (currentSession.value?.session_id === session_id) {
        currentSession.value = null
        messages.value = []
        events.value = []
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  function togglePanel(panel: keyof typeof activePanel) {
    activePanel[panel] = !activePanel[panel]
  }

  return {
    currentSession,
    sessions,
    messages,
    events,
    isLoading,
    activePanel,
    createSession,
    loadSessions,
    selectSession,
    sendMessage,
    stopSession,
    deleteSession,
    togglePanel
  }
}
