<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()
onMounted(() => themeStore.initTheme())
</script>

<style>
@import './assets/styles.css';
</style>
