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
import VMdEditor from '@kangc/v-md-editor'
import '@kangc/v-md-editor/lib/style/base-editor.css'
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js'
import '@kangc/v-md-editor/lib/theme/style/vuepress.css'
import Prism from 'prismjs'
import 'prismjs/themes/prism-okaidia.css'

// 引入 Prism 语言支持
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-typescript'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-css'
import 'prismjs/components/prism-scss'
import 'prismjs/components/prism-java'
import 'prismjs/components/prism-csharp'
import 'prismjs/components/prism-c'
import 'prismjs/components/prism-cpp'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-sql'
import 'prismjs/components/prism-markdown'
import 'prismjs/components/prism-yaml'
import 'prismjs/components/prism-markup'
import 'prismjs/components/prism-go'
import 'prismjs/components/prism-rust'
import 'prismjs/components/prism-docker'
import 'prismjs/components/prism-nginx'
import 'prismjs/components/prism-php'
import 'prismjs/components/prism-ruby'
import 'prismjs/components/prism-swift'
import 'prismjs/components/prism-kotlin'
import 'prismjs/components/prism-perl'
import 'prismjs/components/prism-lua'
import 'prismjs/components/prism-makefile'
import 'prismjs/components/prism-protobuf'
import 'prismjs/components/prism-graphql'

VMdEditor.use(vuepressTheme, {
  Prism
})

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '100%'
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
  '|',
  'undo',
  'redo',
]

const handleSave = () => {
  emit('save', content.value)
}
</script>

<style scoped>
.md-editor-wrapper {
  width: 100%;
  height: 100%;
}

:deep(.v-md-editor__left) {
  border-right: 2px solid #3498db !important;
}

:deep(.v-md-editor__left .v-md-editor__toolbar) {
  border-bottom: 1px solid #e9ecef;
}

:deep(.v-md-editor__right) {
  border-left: none;
}

:deep(.v-md-preview img) {
  max-width: 100%;
  width: auto;
  height: auto;
  display: block;
  border-radius: 4px;
  margin: 16px 0;
  object-fit: contain;
}
</style>
