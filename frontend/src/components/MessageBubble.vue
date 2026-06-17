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
        <div v-if="msg.content" class="content" v-html="rendered"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({ msg: Object })
const showThinking = ref(false)

const rendered = computed(() => {
  if (props.msg.role === 'assistant') {
    return marked.parse(props.msg.content || '')
  }
  return props.msg.content
})
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
  flex-direction: column;
  align-items: flex-end;
}
.assistant .message-inner {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.thinking {
  margin-bottom: 6px;
  width: 100%;
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
  word-break: break-word;
}
.user .bubble {
  background: #2f2f2f;
  color: #e8e8e8;
  padding: 10px 14px;
  border-radius: 18px 18px 4px 18px;
  max-width: 65%;
  align-self: flex-end;
}
.user .bubble .content {
  white-space: pre-wrap;
}
.assistant .bubble {
  background: #2a2a2a;
  color: #d9d9d9;
  padding: 10px 14px;
  border-radius: 4px 18px 18px 18px;
  align-self: flex-start;
  max-width: 85%;
}
.assistant .bubble .content :deep(h1),
.assistant .bubble .content :deep(h2),
.assistant .bubble .content :deep(h3) {
  margin: 12px 0 6px;
  color: #eee;
}
.assistant .bubble .content :deep(h1) { font-size: 20px; }
.assistant .bubble .content :deep(h2) { font-size: 17px; }
.assistant .bubble .content :deep(h3) { font-size: 15px; }
.assistant .bubble .content :deep(p) {
  margin: 6px 0;
}
.assistant .bubble .content :deep(ul),
.assistant .bubble .content :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}
.assistant .bubble .content :deep(li) {
  margin: 3px 0;
}
.assistant .bubble .content :deep(strong) {
  color: #eee;
}
.assistant .bubble .content :deep(code) {
  background: #1a1a1a;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 13px;
  color: #e06c75;
}
.assistant .bubble .content :deep(pre) {
  background: #1a1a1a;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
.assistant .bubble .content :deep(pre code) {
  background: none;
  padding: 0;
  color: #d9d9d9;
}
.assistant .bubble .content :deep(blockquote) {
  border-left: 3px solid #555;
  padding-left: 12px;
  margin: 8px 0;
  color: #999;
}
.assistant .bubble .content :deep(hr) {
  border: none;
  border-top: 1px solid #3a3a3a;
  margin: 12px 0;
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
