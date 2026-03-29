<template>
  <div
    class="mission-page-preview"
    :data-mission-theme="pageThemeId"
    id="mission-print-root"
  >
    <header class="mp-header">
      <p v-if="mission.questCode" class="mp-quest-code">QUEST {{ mission.questCode }}</p>
      <h1 class="mp-title">{{ displayTitle }}</h1>
      <p class="mp-meta-line">
        <template v-if="infoLine">{{ infoLine }}</template>
        <template v-else>&nbsp;</template>
      </p>
      <p v-if="authorsLine" class="mp-authors">{{ authorsLine }}</p>
    </header>

    <section v-if="mission.synopsis" class="mp-block">
      <p class="mp-synopsis">{{ mission.synopsis }}</p>
    </section>

    <section v-if="mission.objectives.length" class="mp-block">
      <h2 class="mp-section-title">Objectifs</h2>
      <ul class="mp-list">
        <li v-for="(item, i) in mission.objectives" :key="'obj-' + i">{{ item }}</li>
      </ul>
    </section>

    <section v-if="mission.specialRules.length" class="mp-block">
      <h2 class="mp-section-title">Règles spéciales</h2>
      <ul class="mp-list">
        <li v-for="(item, i) in mission.specialRules" :key="'sr-' + i">{{ item }}</li>
      </ul>
    </section>

    <section v-if="mission.mapImageDataUrl" class="mp-map-wrap">
      <img :src="mission.mapImageDataUrl" alt="Carte" class="mp-map-img" />
    </section>

    <footer v-if="tilesLine" class="mp-footer">
      <p><strong>Tuiles :</strong> {{ tilesLine }}</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { storeToRefs } from 'pinia'

const mapStore = useMapStore()
const { mission } = storeToRefs(mapStore)

const pageThemeId = computed(() => (mission.value.pageTheme ? mission.value.pageTheme : 'classic'))
const displayTitle = computed(() => (mission.value.title ? mission.value.title : 'Sans titre'))

const infoLine = computed(() => {
  const m = mission.value
  const parts = [m.difficulty, m.playerCount, m.estimatedDuration].filter(Boolean)
  return parts.join(' / ')
})

const authorsLine = computed(() => {
  const a = mission.value.authors
  if (!a || !a.length) return ''
  return 'Par ' + a.join(', ')
})

const tilesLine = computed(() => {
  const t = mission.value.tilesUsed
  if (!t || !t.length) return ''
  return t.join(', ')
})
</script>

<style scoped>
@import url('../assets/mission-print.css');

.mission-page-preview {
  font-family: var(--mp-body);
  color: var(--mp-ink);
  background: var(--mp-bg);
  padding: 1.5rem 1.75rem;
  min-height: 100%;
  box-sizing: border-box;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

.mp-header {
  text-align: center;
  margin-bottom: 1.25rem;
}

.mp-quest-code {
  font-family: var(--mp-body);
  font-size: 0.85rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--mp-accent);
  margin: 0 0 0.25rem;
}

.mp-title {
  font-family: var(--mp-title);
  font-size: 2rem;
  font-weight: normal;
  margin: 0 0 0.5rem;
  line-height: 1.15;
  color: var(--mp-accent);
}

.mp-meta-line {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin: 0;
}

.mp-authors {
  font-size: 0.95rem;
  font-style: italic;
  margin: 0.85rem 0 0;
  opacity: 0.9;
}

.mp-block {
  margin-bottom: 1.25rem;
}

.mp-synopsis {
  margin: 0;
  line-height: 1.55;
  white-space: pre-wrap;
}

.mp-section-title {
  font-family: var(--mp-title);
  font-size: 1.35rem;
  font-weight: normal;
  margin: 0 0 0.5rem;
  color: var(--mp-accent);
}

.mp-list {
  margin: 0;
  padding-left: 1.25rem;
  line-height: 1.5;
}

.mp-list li {
  margin-bottom: 0.35rem;
}

.mp-map-wrap {
  margin: 1rem 0;
  text-align: center;
}

.mp-map-img {
  max-width: 100%;
  height: auto;
  border: 2px solid var(--mp-accent);
  border-radius: 4px;
}

.mp-footer {
  margin-top: 1rem;
  font-size: 0.9rem;
  border-top: 1px solid color-mix(in srgb, var(--mp-ink) 25%, transparent);
  padding-top: 0.75rem;
}
</style>