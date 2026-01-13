<template>
  <div class="min-h-screen flex">
    <aside class="w-64 bg-gray-900 text-white p-4 flex flex-col">
      <div class="mb-6">
        <h1 class="text-xl font-bold">Manus AI</h1>
        <p class="text-sm text-gray-400">LangChain + LangGraph</p>
      </div>

      <button
        @click="createNewSession"
        class="mb-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
      >
        + New Session
      </button>

      <div class="flex-1 overflow-y-auto">
        <div
          v-for="session in sessions"
          :key="session.session_id"
          @click="selectSession(session.session_id)"
          class="mb-2 p-3 rounded cursor-pointer hover:bg-gray-800"
          :class="{ 'bg-gray-800': currentSession?.session_id === session.session_id }"
        >
          <div class="font-medium truncate">{{ session.title }}</div>
          <div class="text-xs text-gray-400">{{ formatDate(session.created_at) }}</div>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col">
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="messages.length === 0" class="text-center text-gray-400 mt-20">
          <p class="text-4xl mb-4">🤖</p>
          <p>Start a conversation with Manus AI Agent</p>
        </div>

        <div v-else class="max-w-4xl mx-auto space-y-4">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="p-4 rounded-lg"
            :class="message.role === 'user' ? 'bg-blue-100 ml-12' : 'bg-gray-100 mr-12'"
          >
            <div class="font-medium mb-2">
              {{ message.role === 'user' ? 'You' : 'Agent' }}
            </div>
            <div class="text-gray-700" v-html="renderMarkdown(message.content)"></div>
          </div>
        </div>
      </div>

      <div class="border-t p-4">
        <div class="max-w-4xl mx-auto flex gap-2">
          <input
            v-model="inputMessage"
            @keyup.enter="send"
            :disabled="isLoading"
            placeholder="Type your message..."
            class="flex-1 border rounded px-4 py-2"
          />

          <button
            @click="send"
            :disabled="isLoading || !inputMessage.trim()"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded"
          >
            {{ isLoading ? '...' : 'Send' }}
          </button>

          <button
            v-if="currentSession"
            @click="stopSession"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
          >
            Stop
          </button>
        </div>
      </div>
    </main>

    <aside class="w-80 bg-gray-100 p-4 overflow-y-auto">
      <div class="space-y-4">
        <div class="mb-4">
          <h2 class="font-bold mb-2">Events</h2>
          <div class="space-y-2 max-h-40 overflow-y-auto">
            <div
              v-for="(event, index) in events.slice(-10)"
              :key="index"
              class="p-2 bg-white rounded text-sm"
            >
              <div class="font-medium">{{ event.event_type }}</div>
              <div v-if="event.step" class="text-gray-600">{{ event.step }}</div>
              <div v-if="event.message" class="text-gray-600">{{ event.message }}</div>
            </div>
          </div>
        </div>

        <div class="mb-4">
          <button
            @click="togglePanel('browser')"
            class="w-full text-left px-3 py-2 rounded hover:bg-gray-200"
          >
            🌐 Browser
          </button>
          <button
            @click="togglePanel('shell')"
            class="w-full text-left px-3 py-2 rounded hover:bg-gray-200"
          >
            💻 Shell
          </button>
          <button
            @click="togglePanel('file')"
            class="w-full text-left px-3 py-2 rounded hover:bg-gray-200"
          >
            📁 File
          </button>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChat } from '@/composables/useChat'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const {
  currentSession,
  sessions,
  messages,
  events,
  isLoading,
  activePanel,
  createSession: createNewSession,
  loadSessions,
  selectSession,
  sendMessage,
  stopSession,
  deleteSession,
  togglePanel
} = useChat()

const inputMessage = ref('')

function renderMarkdown(content: string) {
  const html = marked(content)
  return DOMPurify.sanitize(html)
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleString()
}

async function send() {
  if (!inputMessage.value.trim() || isLoading.value) return

  const message = inputMessage.value
  inputMessage.value = ''

  await sendMessage(message)
}

onMounted(() => {
  loadSessions()
})
</script>

<style>
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}
</style>
