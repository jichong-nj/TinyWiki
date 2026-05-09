<template>
  <div class="md-editor-wrapper">
    <v-md-editor
      v-model="content"
      :height="height"
      :toolbar="toolbar"
      :mode="mode"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '600px'
  },
  mode: {
    type: String,
    default: 'split'
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const content = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  content.value = newVal
})

watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

const toolbar = [
  'undo',
  'redo',
  '|',
  'bold',
  'italic',
  'header',
  'underline',
  'strikethrough',
  '|',
  'h1',
  'h2',
  'h3',
  '|',
  'quote',
  'list',
  'ordered-list',
  'task',
  '|',
  'code',
  'link',
  'image',
  'table',
]

const handleSave = () => {
  emit('save', content.value)
}
</script>

<style scoped>
.md-editor-wrapper {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>