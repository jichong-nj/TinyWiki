<template>
  <div class="app-container">
    <RouterView />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>

<script>
import { ref, onMounted } from 'vue'
import ribbon from './components/ribbon.js'
export default {
  setup() {
    const message = ref('你好，wps加载项')
    onMounted(() => {
      window.ribbon = ribbon
    })

    return {
      message
    }
  }
}
</script>

