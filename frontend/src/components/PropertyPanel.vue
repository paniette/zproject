<template>
  <aside class="property-panel">
    <h3 class="panel-title">Propriétés</h3>
    <p v-if="mapStore.isPreviewMode" class="preview-hint">Aperçu actif — propriétés en lecture seule.</p>
    <div v-if="!selectionId" class="empty-state">
      Sélectionnez une tuile ou un objet sur la carte pour éditer position, rotation et données.
    </div>
    <div v-else-if="kind === 'tile' && tile" class="form">
      <p class="badge">Tuile</p>
      <label>Asset</label>
      <p class="readonly">{{ shortPath(tile.asset) }}</p>
      <label for="pp-tx">X (grille)</label>
      <input id="pp-tx" v-model.number="localX" type="number" class="inp" :disabled="mapStore.isPreviewMode" @change="applyTile" />
      <label for="pp-ty">Y (grille)</label>
      <input id="pp-ty" v-model.number="localY" type="number" class="inp" :disabled="mapStore.isPreviewMode" @change="applyTile" />
      <label for="pp-tr">Rotation (°)</label>
      <input id="pp-tr" v-model.number="localRot" type="number" class="inp" step="90" :disabled="mapStore.isPreviewMode" @change="applyTile" />
    </div>
    <div v-else-if="kind === 'object' && obj" class="form">
      <p class="badge">Objet</p>
      <label>Type</label>
      <p class="readonly">{{ obj.type }}</p>
      <label>Asset</label>
      <p class="readonly">{{ shortPath(obj.asset) }}</p>
      <label for="pp-ox">X (grille)</label>
      <input id="pp-ox" v-model.number="localX" type="number" class="inp" :disabled="mapStore.isPreviewMode" @change="applyObject" />
      <label for="pp-oy">Y (grille)</label>
      <input id="pp-oy" v-model.number="localY" type="number" class="inp" :disabled="mapStore.isPreviewMode" @change="applyObject" />
      <label for="pp-or">Rotation (°)</label>
      <input id="pp-or" v-model.number="localRot" type="number" class="inp" step="90" :disabled="mapStore.isPreviewMode" @change="applyObject" />
      <label for="pp-props">Propriétés (JSON)</label>
      <textarea id="pp-props" v-model="propsJson" class="textarea" rows="5" spellcheck="false" :disabled="mapStore.isPreviewMode" @change="applyPropsJson" />
      <p v-if="propsError" class="error">{{ propsError }}</p>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useToolStore } from '@/stores/toolStore'

const mapStore = useMapStore()
const toolStore = useToolStore()

const selectionId = computed(() => toolStore.selectedObject)

const tile = computed(() =>
  selectionId.value ? mapStore.layers.tiles.find(t => t.id === selectionId.value) : null
)
const obj = computed(() =>
  selectionId.value ? mapStore.layers.objects.find(o => o.id === selectionId.value) : null
)
const kind = computed(() => {
  if (tile.value) return 'tile'
  if (obj.value) return 'object'
  return null
})

const localX = ref(0)
const localY = ref(0)
const localRot = ref(0)
const propsJson = ref('{}')
const propsError = ref('')

function shortPath (p) {
  if (!p) return '—'
  const s = String(p)
  return s.length > 42 ? '…' + s.slice(-40) : s
}

function syncFromSelection () {
  propsError.value = ''
  const t = tile.value
  const o = obj.value
  if (t) {
    localX.value = t.x
    localY.value = t.y
    localRot.value = t.rotation ?? 0
  } else if (o) {
    localX.value = o.x
    localY.value = o.y
    localRot.value = o.rotation ?? 0
    try {
      propsJson.value = JSON.stringify(o.properties && typeof o.properties === 'object' ? o.properties : {}, null, 2)
    } catch {
      propsJson.value = '{}'
    }
  }
}

watch(
  [selectionId, () => tile.value, () => obj.value],
  () => syncFromSelection(),
  { immediate: true }
)

function applyTile () {
  if (!tile.value) return
  mapStore.updateTile(tile.value.id, {
    x: Math.round(Number(localX.value) || 0),
    y: Math.round(Number(localY.value) || 0),
    rotation: Number(localRot.value) || 0
  })
}

function applyObject () {
  if (!obj.value) return
  mapStore.updateObject(obj.value.id, {
    x: Math.round(Number(localX.value) || 0),
    y: Math.round(Number(localY.value) || 0),
    rotation: Number(localRot.value) || 0
  })
}

function applyPropsJson () {
  if (!obj.value) return
  try {
    const parsed = JSON.parse(propsJson.value || '{}')
    if (typeof parsed !== 'object' || parsed === null) throw new Error('Le JSON doit être un objet')
    propsError.value = ''
    mapStore.updateObject(obj.value.id, { properties: parsed })
  } catch (e) {
    propsError.value = e.message || 'JSON invalide'
  }
}
</script>

<style scoped>
.property-panel {
  width: 260px;
  min-width: 220px;
  max-width: 320px;
  background: linear-gradient(180deg, var(--brown-dark) 0%, var(--gray-dark) 100%);
  color: #fff;
  border-left: 2px solid var(--primary-color);
  padding: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}

.panel-title {
  font-family: 'Creepster', cursive;
  font-size: 1.25rem;
  margin: 0 0 12px;
  color: var(--primary-color);
}

.preview-hint {
  font-size: 0.8rem;
  margin: 0 0 10px;
  padding: 6px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--brown-light);
}

.empty-state {
  font-size: 0.9rem;
  line-height: 1.45;
  opacity: 0.85;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.badge {
  margin: 0 0 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--brown-light);
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 4px;
}

.readonly {
  margin: 0;
  font-size: 0.85rem;
  word-break: break-all;
  opacity: 0.9;
}

.inp,
.textarea {
  padding: 6px 8px;
  border-radius: 4px;
  border: 1px solid var(--brown-light);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 0.9rem;
}

.textarea {
  font-family: ui-monospace, monospace;
  resize: vertical;
}

.error {
  color: #ffb4b4;
  font-size: 0.8rem;
  margin: 0;
}
</style>
