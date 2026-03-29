<template>
  <div class="editor-layout">
    <AppHeader />
    <div class="editor-stack">
      <MapEditor v-show="isMap" class="editor-main" />
      <MissionEditor v-show="!isMap" class="editor-main" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './AppHeader.vue'
import MapEditor from './MapEditor.vue'
import MissionEditor from './MissionEditor.vue'

const route = useRoute()
const isMap = computed(() => route.name === 'MapEditor')
</script>

<style scoped>
.editor-layout {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.editor-stack {
  flex: 1;
  min-height: 0;
  position: relative;
}
.editor-main {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
</style>