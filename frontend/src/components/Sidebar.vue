<template>
  <div class="sidebar">
    <div class="sidebar-top">
      <button class="btn-new" @click="$emit('new')">+ 新对话</button>
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
        <button class="btn-del" @click="$emit('delete', c.id)">×</button>
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
  background: #1e1e2e;
  color: #cdd6f4;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.sidebar-top {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.btn-new {
  background: #45475a;
  color: #cdd6f4;
  border: none;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.btn-new:hover { background: #585b70; }
select {
  background: #45475a;
  color: #cdd6f4;
  border: none;
  padding: 8px;
  border-radius: 6px;
  font-size: 14px;
}
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 12px;
}
.conv-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 4px;
  cursor: pointer;
}
.conv-item:hover { background: #313244; }
.conv-item.active { background: #45475a; }
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
  color: #6c7086;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
}
.btn-del:hover { color: #f38ba8; }
.empty { color: #6c7086; font-size: 13px; text-align: center; margin-top: 20px; }
</style>
