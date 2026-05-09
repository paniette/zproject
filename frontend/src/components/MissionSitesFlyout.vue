<template>
  <div
    ref="rootRef"
    class="mission-sites-flyout"
    @mouseenter="onRootMouseEnter"
    @mouseleave="onRootMouseLeave"
    @focusin="onFocusIn"
    @focusout="onFocusOut"
  >
    <button
      ref="triggerRef"
      type="button"
      class="mission-sites-logo-btn"
      :class="{ 'is-open': panelOpen }"
      :aria-expanded="panelOpen"
      aria-haspopup="true"
      :aria-controls="panelId"
      @click="onTriggerClick"
    >
      <slot />
    </button>
    <div
      v-show="panelOpen"
      :id="panelId"
      class="mission-sites-panel"
      role="region"
      :aria-label="$t('missionSites.panelTitle')"
      @mousedown.stop
    >
      <p class="mission-sites-intro">{{ $t('missionSites.panelTitle') }}</p>
      <ul class="mission-sites-list">
        <li v-for="entry in MISSION_SITE_ENTRIES" :key="entry.id" class="mission-sites-item">
          <img
            class="mission-sites-thumb"
            :src="entry.thumb"
            width="160"
            height="100"
            loading="lazy"
            alt=""
          />
          <div class="mission-sites-body">
            <a
              class="mission-sites-link"
              :href="entry.url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ $t(`missionSites.sites.${entry.id}.title`) }}
            </a>
            <p class="mission-sites-desc">
              {{ $t(`missionSites.sites.${entry.id}.description`) }}
            </p>
            <a
              class="mission-sites-external"
              :href="entry.url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ $t('missionSites.openSite') }}
            </a>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { MISSION_SITE_ENTRIES } from '@/config/missionSites'

const panelId = 'mission-sites-flyout-panel'

const rootRef = ref(null)
const triggerRef = ref(null)

const hoverOpen = ref(false)
const pinnedOpen = ref(false)
const focusInside = ref(false)
/** Après Échap : masquer le panneau même si le focus reste sur le déclencheur. */
const dismissed = ref(false)

let leaveTimer = null

function clearLeaveTimer () {
  if (leaveTimer) {
    clearTimeout(leaveTimer)
    leaveTimer = null
  }
}

function onRootMouseEnter () {
  dismissed.value = false
  clearLeaveTimer()
  hoverOpen.value = true
}

function onRootMouseLeave () {
  clearLeaveTimer()
  leaveTimer = window.setTimeout(() => {
    hoverOpen.value = false
    leaveTimer = null
  }, 220)
}

function prefersFinePointerHover () {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(hover: hover) and (pointer: fine)').matches
}

function onTriggerClick () {
  if (prefersFinePointerHover()) return
  dismissed.value = false
  pinnedOpen.value = !pinnedOpen.value
}

function onFocusIn () {
  dismissed.value = false
  focusInside.value = true
}

function onFocusOut () {
  nextTick(() => {
    const root = rootRef.value
    if (!root || !document.activeElement || !root.contains(document.activeElement)) {
      focusInside.value = false
    }
  })
}

const panelOpen = computed(() => {
  if (dismissed.value) return false
  return hoverOpen.value || pinnedOpen.value || focusInside.value
})

function closePanel () {
  dismissed.value = true
  hoverOpen.value = false
  pinnedOpen.value = false
  triggerRef.value?.focus()
}

function onDocumentPointerDown (e) {
  const root = rootRef.value
  if (!root || root.contains(e.target)) return
  if (pinnedOpen.value) pinnedOpen.value = false
}

function onDocumentKeydown (e) {
  if (e.key !== 'Escape') return
  if (!panelOpen.value) return
  e.preventDefault()
  closePanel()
}

onMounted(() => {
  document.addEventListener('pointerdown', onDocumentPointerDown, true)
  document.addEventListener('keydown', onDocumentKeydown, true)
})

onBeforeUnmount(() => {
  clearLeaveTimer()
  document.removeEventListener('pointerdown', onDocumentPointerDown, true)
  document.removeEventListener('keydown', onDocumentKeydown, true)
})
</script>

<style scoped>
.mission-sites-flyout {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.mission-sites-logo-btn {
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: 'Creepster', cursive;
  font-size: 1.8rem;
  font-weight: normal;
  color: var(--primary-color);
  line-height: 1.2;
  text-align: left;
}

.mission-sites-logo-btn:hover,
.mission-sites-logo-btn:focus-visible {
  color: color-mix(in srgb, var(--primary-color) 88%, white);
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.mission-sites-logo-btn.is-open {
  color: color-mix(in srgb, var(--primary-color) 75%, white);
}

.mission-sites-panel {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 1300;
  width: min(420px, calc(100vw - 24px));
  max-height: min(70vh, 520px);
  overflow-y: auto;
  padding: 12px 14px;
  border-radius: 8px;
  border: 2px solid var(--brown-light);
  background: linear-gradient(145deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45);
  color: rgba(255, 255, 255, 0.92);
}

.mission-sites-intro {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
}

.mission-sites-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mission-sites-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.mission-sites-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.mission-sites-thumb {
  flex-shrink: 0;
  width: 88px;
  height: auto;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  object-fit: cover;
  background: #1a1816;
}

.mission-sites-body {
  min-width: 0;
  flex: 1;
}

.mission-sites-link {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
}

.mission-sites-link:hover {
  text-decoration: underline;
  color: var(--primary-color);
}

.mission-sites-desc {
  margin: 4px 0 6px;
  font-size: 12px;
  line-height: 1.35;
  color: rgba(255, 255, 255, 0.78);
}

.mission-sites-external {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color);
  text-decoration: none;
}

.mission-sites-external:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .mission-sites-logo-btn {
    font-size: 1.35rem;
  }

  .mission-sites-panel {
    left: 0;
    right: auto;
    width: min(100vw - 16px, 400px);
    max-width: none;
  }

  .mission-sites-item {
    flex-direction: column;
  }

  .mission-sites-thumb {
    width: 100%;
    max-height: 120px;
    object-fit: cover;
  }
}
</style>
