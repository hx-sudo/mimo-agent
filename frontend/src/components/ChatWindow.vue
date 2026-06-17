<template>
  <div class="chat">
    <div class="chat-body" ref="bodyRef">
      <div v-if="!messages.length" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="1.5"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        </div>
        <h2>开始新对话</h2>
        <p>输入问题或上传图片开始聊天</p>
      </div>
      <MessageBubble v-for="(msg, i) in messages" :key="i" :msg="msg" />
      <div v-if="loading" class="typing">
        <span class="dot-indicator"><span></span><span></span><span></span></span>
      </div>
    </div>
    <div v-if="imagePreview" class="image-preview">
      <img :src="imagePreview" />
      <button class="btn-remove-img" @click="removeImage">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="input-area">
      <div class="input-box">
        <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="onImageSelected" />
        <button class="btn-attach" @click="$refs.fileInput.click()" :disabled="loading" title="上传图片">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
        </button>
        <input
          v-model="input"
          @keydown.enter="send"
          placeholder="发送消息..."
          :disabled="loading"
        />
        <button class="btn-send" @click="send" :disabled="loading || (!input.trim() && !imageData)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
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
const fileInput = ref(null)
const imagePreview = ref(null)
const imageData = ref(null)

function onImageSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    imagePreview.value = ev.target.result
    imageData.value = ev.target.result
  }
  reader.readAsDataURL(file)
}

function removeImage() {
  imagePreview.value = null
  imageData.value = null
  fileInput.value.value = ''
}

function send() {
  const text = input.value.trim()
  if (!text && !imageData.value) return
  emit('send', text || '请描述这张图片', imageData.value ? [imageData.value] : [])
  input.value = ''
  removeImage()
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
  background: #212121;
  min-width: 0;
}
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  gap: 12px;
}
.empty-state h2 { font-size: 20px; font-weight: 500; color: #aaa; }
.empty-state p { font-size: 14px; color: #666; }
.typing {
  padding: 16px 0 8px;
  display: flex;
  justify-content: flex-start;
  padding-left: 48px;
}
.dot-indicator {
  display: flex;
  gap: 4px;
}
.dot-indicator span {
  width: 6px;
  height: 6px;
  background: #888;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}
.dot-indicator span:nth-child(1) { animation-delay: 0s; }
.dot-indicator span:nth-child(2) { animation-delay: 0.2s; }
.dot-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
.input-area {
  padding: 16px 24px 24px;
}
.input-box {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #2f2f2f;
  border: 1px solid #3a3a3a;
  border-radius: 12px;
  padding: 8px 12px;
  transition: border-color 0.2s;
}
.input-box:focus-within { border-color: #555; }
.input-box input[type="text"], .input-box input:not([type]) {
  flex: 1;
  background: transparent;
  border: none;
  color: #ececec;
  padding: 6px 8px;
  font-size: 15px;
  outline: none;
}
.input-box input::placeholder { color: #666; }
.btn-attach {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  color: #888;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}
.btn-attach:hover { color: #ccc; background: #3a3a3a; }
.btn-attach:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-send {
  background: #fff;
  color: #000;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 0.15s;
}
.btn-send:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-send:hover:not(:disabled) { opacity: 0.85; }
.image-preview {
  position: relative;
  padding: 0 24px 8px;
}
.image-preview img {
  max-height: 120px;
  border-radius: 8px;
}
.btn-remove-img {
  position: absolute;
  top: -4px;
  right: 28px;
  background: #333;
  color: #ccc;
  border: 1px solid #444;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.btn-remove-img:hover { background: #ef4444; color: #fff; border-color: #ef4444; }
</style>
