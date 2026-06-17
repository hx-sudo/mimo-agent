<template>
  <div class="message" :class="msg.role">
    <div class="message-inner">
      <div v-if="msg.role === 'assistant' && msg.thinking" class="thinking" @click="showThinking = !showThinking">
        <span class="thinking-toggle">{{ showThinking ? '▼' : '▶' }} 思考过程</span>
        <pre v-if="showThinking" class="thinking-content">{{ msg.thinking }}</pre>
      </div>
      <div class="bubble">
        <div v-if="msg.images && msg.images.length" class="images">
          <img v-for="(img, i) in msg.images" :key="i" :src="img" />
        </div>
        <div v-if="msg.content" class="content">{{ msg.content }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ msg: Object })
const showThinking = ref(false)
</script>

<style scoped>
.message {
  padding: 6px 0;
}
.message-inner {
  max-width: 760px;
  margin: 0 auto;
  padding: 0 24px;
}
.user .message-inner {
  display: flex;
  justify-content: flex-end;
}
.assistant .message-inner {
  display: flex;
  justify-content: flex-start;
}
.thinking {
  margin-bottom: 6px;
}
.thinking-toggle {
  font-size: 12px;
  color: #666;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
}
.thinking-toggle:hover { color: #999; }
.thinking-content {
  margin-top: 6px;
  padding: 10px 12px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  font-size: 12px;
  color: #888;
  max-height: 180px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.5;
}
.bubble {
  font-size: 15px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}
.user .bubble {
  background: #2f2f2f;
  color: #e8e8e8;
  padding: 10px 14px;
  border-radius: 18px 18px 4px 18px;
  max-width: 65%;
}
.assistant .bubble {
  background: transparent;
  color: #d9d9d9;
  padding: 4px 0;
}
.images {
  margin-bottom: 6px;
}
.images img {
  max-width: 240px;
  max-height: 240px;
  border-radius: 10px;
  display: block;
}
.user .images img {
  margin-bottom: 4px;
}
</style>
