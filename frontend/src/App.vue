<template>
  <div class="app">
    <Sidebar
      :conversations="conversations"
      :currentId="currentConvId"
      :models="models"
      :currentModel="currentModel"
      @new="newConversation"
      @select="selectConversation"
      @delete="removeConversation"
      @modelChange="currentModel = $event"
    />
    <ChatWindow
      :messages="messages"
      :title="currentTitle"
      :loading="loading"
      @send="handleSend"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatWindow from './components/ChatWindow.vue'
import {
  fetchModels, fetchConversations, loadConversation,
  saveConversation, deleteConversation, sendMessage,
} from './api.js'

const models = ref([])
const currentModel = ref('')
const conversations = ref([])
const currentConvId = ref(null)
const currentTitle = ref('新对话')
const messages = ref([])
const loading = ref(false)

onMounted(async () => {
  const data = await fetchModels()
  models.value = data.models
  currentModel.value = data.default
  conversations.value = await fetchConversations()
})

async function selectConversation(id) {
  const data = await loadConversation(id)
  currentConvId.value = id
  currentTitle.value = data.title
  messages.value = data.messages || []
  if (data.model) currentModel.value = data.model
}

function newConversation() {
  currentConvId.value = null
  currentTitle.value = '新对话'
  messages.value = []
}

async function removeConversation(id) {
  await deleteConversation(id)
  conversations.value = await fetchConversations()
  if (currentConvId.value === id) newConversation()
}

async function handleSend(text, images = []) {
  loading.value = true
  messages.value.push({ role: 'user', content: text, images })

  try {
    const result = await sendMessage(text, messages.value, currentModel.value, images)
    messages.value.push({
      role: 'assistant',
      content: result.content,
      thinking: result.thinking || '',
    })

    const id = currentConvId.value || null
    const title = currentTitle.value === '新对话'
      ? text.slice(0, 30) + (text.length > 30 ? '...' : '')
      : currentTitle.value
    const saved = await saveConversation(id, title, messages.value, currentModel.value)
    currentConvId.value = saved.id
    currentTitle.value = saved.title
    conversations.value = await fetchConversations()
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '出错了: ' + e.message })
  } finally {
    loading.value = false
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #212121;
  color: #ececec;
}
.app { display: flex; height: 100vh; overflow: hidden; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #424242; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
