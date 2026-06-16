<template>
  <div class="chat">
    <div class="chat-header">{{ title }}</div>
    <div class="chat-body" ref="bodyRef">
      <MessageBubble v-for="(msg, i) in messages" :key="i" :msg="msg" />
      <div v-if="loading" class="typing"><span class="dots">思考中<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span></div>
    </div>
    <div class="chat-input">
      <input
        v-model="input"
        @keydown.enter="send"
        placeholder="输入你的问题..."
        :disabled="loading"
      />
      <button @click="send" :disabled="loading || !input.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({
  messages: Array,
  title: String,
  loading: Boolean,
})
const emit = defineEmits(['send'])

const input = ref('')
const bodyRef = ref(null)

function send() {
  const text = input.value.trim()
  if (!text) return
  emit('send', text)
  input.value = ''
}

watch(() => props.messages.length, () => {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  })
})
</script>

<style scoped>
.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #181825;
}
.chat-header {
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  color: #cdd6f4;
  border-bottom: 1px solid #313244;
}
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.typing {
  color: #6c7086;
  font-size: 14px;
  padding: 8px 0;
}
.dots .dot {
  animation: blink 1.4s infinite both;
}
.dots .dot:nth-child(2) { animation-delay: 0.2s; }
.dots .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}
.chat-input {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #313244;
}
.chat-input input {
  flex: 1;
  background: #313244;
  border: none;
  color: #cdd6f4;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}
.chat-input input::placeholder { color: #6c7086; }
.chat-input button {
  background: #89b4fa;
  color: #1e1e2e;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 600;
}
.chat-input button:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-input button:hover:not(:disabled) { background: #74c7ec; }
</style>
