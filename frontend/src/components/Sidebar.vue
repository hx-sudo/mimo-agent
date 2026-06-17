<template>
  <div class="sidebar">
    <div class="sidebar-top">
      <button class="btn-new" @click="$emit('new')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新对话
      </button>
      <select :value="currentModel" @change="$emit('modelChange', $event.target.value)">
        <option v-for="m in models" :key="m.name" :value="m.name">{{ m.label }}</option>
      </select>
    </div>
    <div class="conv-list">
      <div
        v-for="c in conversations"
        :key="c.id"
        class="conv-item"
        :class="{ active: c.id === currentId }"
      >
        <span class="conv-title" @click="$emit('select', c.id)">{{ c.title }}</span>
        <button class="btn-del" @click="$emit('delete', c.id)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <p v-if="!conversations.length" class="empty">暂无对话</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conversations: Array,
  currentId: String,
  models: Array,
  currentModel: String,
})
defineEmits(['new', 'select', 'delete', 'modelChange'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #171717;
  color: #ececec;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-right: 1px solid #2a2a2a;
}
.sidebar-top {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.btn-new {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: transparent;
  color: #ececec;
  border: 1px solid #3a3a3a;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s;
}
.btn-new:hover { background: #2a2a2a; }
select {
  background: #2a2a2a;
  color: #ececec;
  border: 1px solid #3a3a3a;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  outline: none;
}
select:focus { border-color: #555; }
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px 8px;
}
.conv-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 2px;
  cursor: pointer;
  transition: background 0.15s;
}
.conv-item:hover { background: #2a2a2a; }
.conv-item.active { background: #333; }
.conv-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}
.btn-del {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
}
.conv-item:hover .btn-del { opacity: 1; }
.btn-del:hover { color: #ef4444; }
.empty { color: #666; font-size: 13px; text-align: center; margin-top: 24px; }
</style>
