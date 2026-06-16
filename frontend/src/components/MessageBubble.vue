<template>
  <div class="bubble" :class="msg.role">
    <div v-if="msg.thinking" class="thinking" @click="showThinking = !showThinking">
      {{ showThinking ? '▼' : '▶' }} 思考过程
      <pre v-if="showThinking">{{ msg.thinking }}</pre>
    </div>
    <div v-if="msg.images && msg.images.length" class="images">
      <img v-for="(img, i) in msg.images" :key="i" :src="img" />
    </div>
    <div class="content">{{ msg.content }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ msg: Object })
const showThinking = ref(false)
</script>

<style scoped>
.bubble {
  max-width: 75%;
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.user {
  background: #89b4fa;
  color: #1e1e2e;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}
.assistant {
  background: #313244;
  color: #cdd6f4;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}
.thinking {
  font-size: 12px;
  color: #a6adc8;
  margin-bottom: 6px;
  cursor: pointer;
}
.thinking pre {
  margin-top: 4px;
  padding: 8px;
  background: #1e1e2e;
  border-radius: 6px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
}
.content { white-space: pre-wrap; }
.images {
  margin-bottom: 8px;
}
.images img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  display: block;
}
</style>
