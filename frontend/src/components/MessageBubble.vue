<template>
  <div class="message" :class="msg.role">
    <div class="message-inner">
      <div v-if="msg.thinking" class="thinking" @click="showThinking = !showThinking">
        <span class="thinking-toggle">{{ showThinking ? '▼' : '▶' }} 思考过程</span>
        <pre v-if="showThinking" class="thinking-content">{{ msg.thinking }}</pre>
      </div>
      <div v-if="msg.images && msg.images.length" class="images">
        <img v-for="(img, i) in msg.images" :key="i" :src="img" />
      </div>
      <div class="content">{{ msg.content }}</div>
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
  padding: 16px 0;
}
.message-inner {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 24px;
  font-size: 15px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}
.user .message-inner {
  display: flex;
  justify-content: flex-end;
}
.user .message-inner .content {
  background: #2f2f2f;
  color: #ececec;
  padding: 10px 16px;
  border-radius: 16px 16px 4px 16px;
  max-width: 70%;
}
.assistant .message-inner {
  color: #d4d4d4;
}
.thinking {
  margin-bottom: 8px;
}
.thinking-toggle {
  font-size: 13px;
  color: #888;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
}
.thinking-toggle:hover { color: #bbb; }
.thinking-content {
  margin-top: 8px;
  padding: 12px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  font-size: 13px;
  color: #999;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: inherit;
}
.images {
  margin-bottom: 8px;
}
.images img {
  max-width: 240px;
  max-height: 240px;
  border-radius: 8px;
  display: block;
}
</style>
