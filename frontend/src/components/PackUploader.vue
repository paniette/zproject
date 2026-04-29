<template>
  <div v-if="show" class="pack-uploader-overlay" @click.self="close">
    <div class="pack-uploader">
      <div class="modal-header">
        <h3>Upload d'Asset Personnalisé</h3>
        <button type="button" @click="close" class="close-btn" aria-label="Fermer">×</button>
      </div>
      <form @submit.prevent="uploadAsset" class="upload-form">
        <div class="form-group">
          <label>Fichier image</label>
          <input
            ref="fileInputRef"
            type="file"
            @change="handleFileSelect"
            accept="image/*"
            required
          />
          <div v-if="previewImage" class="preview">
            <img :src="previewImage" alt="Aperçu" />
          </div>
        </div>

        <div class="form-group">
          <label for="asset-kind">Type (préréglage)</label>
          <select id="asset-kind" v-model="assetKind" class="full-width">
            <option v-for="opt in assetKindOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }} ({{ opt.w }}×{{ opt.h }} px)
            </option>
          </select>
          <p class="hint">La liste ou les mini-boutons ci-dessous pré-remplissent largeur et hauteur ; tu peux les ajuster à la main.</p>
          <div class="preset-row" role="group" aria-label="Préréglages de taille discrets">
            <span class="preset-hint" title="Un clic applique la taille dans les champs">Tailles courantes</span>
            <button
              v-for="opt in assetKindOptions"
              :key="'p-' + opt.value"
              type="button"
              class="preset-chip"
              :class="{ active: assetKind === opt.value }"
              :title="opt.tooltip"
              @click="applyKindFromOption(opt)"
            >
              {{ opt.shortLabel }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Dimensions finales (utilisées pour l’upload)</label>
          <div class="dim-inputs">
            <div>
              <label for="target-w">Largeur (px)</label>
              <input
                id="target-w"
                v-model.number="targetW"
                type="number"
                min="8"
                max="2048"
                required
              />
            </div>
            <div>
              <label for="target-h">Hauteur (px)</label>
              <input
                id="target-h"
                v-model.number="targetH"
                type="number"
                min="8"
                max="2048"
                required
              />
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Nom de l'asset</label>
          <input v-model="assetName" type="text" required placeholder="ex. MonTuile.png" />
        </div>

        <template v-if="isContextual">
          <div class="form-group contextual-info">
            <label>Pack</label>
            <p class="readonly-field">{{ contextualPackTitle }}</p>
            <label>Type de jeu</label>
            <select v-model="gameType" class="full-width">
              <option v-for="t in GAME_TYPES" :key="'gt-' + t.id" :value="t.id" :disabled="t.id === 'all'">
                {{ t.label }}
              </option>
            </select>
            <label>Catégorie</label>
            <p class="readonly-field">{{ category }}</p>
          </div>
        </template>
        <template v-else>
          <div class="form-group">
            <label>Pack</label>
            <select v-model="packName" @change="loadPackCategories" required>
              <option value="">Sélectionner un pack</option>
              <option v-for="pack in availablePacks" :key="pack.id" :value="pack.id">
                {{ pack.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Type de jeu</label>
            <select v-model="gameType" class="full-width">
              <option v-for="t in GAME_TYPES" :key="'gt-' + t.id" :value="t.id" :disabled="t.id === 'all'">
                {{ t.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Catégorie</label>
            <select v-model="category" :disabled="!packName || categories.length === 0" required>
              <option value="">Sélectionner une catégorie</option>
              <option v-for="cat in categories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>
        </template>

        <button type="submit" :disabled="uploading || !packName || !category" class="submit-btn">
          {{ uploading ? 'Upload en cours...' : 'Upload et Normaliser' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/services/api'
import { GAME_TYPES, loadPackGameTypeMap, savePackGameTypeMap, getPackGameType } from '@/config/gameTypes'

/** Tailles courantes pour upload assisté (issue #10) — tooltips sur les mini-boutons */
const assetKindOptions = [
  {
    value: 'tile',
    label: 'Tuile',
    shortLabel: '250²',
    w: 250,
    h: 250,
    tooltip: 'Tuile : 250×250 px'
  },
  {
    value: 'pop',
    label: 'Point de pop',
    shortLabel: '56×26',
    w: 56,
    h: 26,
    tooltip: 'Point de pop (spawn) : 56×26 px'
  },
  {
    value: 'character',
    label: 'Personnage',
    shortLabel: '30×50',
    w: 30,
    h: 50,
    tooltip: 'Personnage / figurine : 30×50 px'
  },
  {
    value: 'token',
    label: 'Jeton',
    shortLabel: '35²',
    w: 35,
    h: 35,
    tooltip: 'Jeton : 35×35 px'
  }
]

const props = defineProps({
  show: {
    type: Boolean,
    default: true
  },
  packId: {
    type: String,
    default: ''
  },
  categoryPreset: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'uploaded'])

const close = () => {
  emit('close')
}

const isContextual = computed(
  () => !!(props.packId && props.categoryPreset)
)

const contextualPackTitle = computed(() => {
  const p = availablePacks.value.find((x) => x.id === packName.value)
  return p?.name || packName.value || props.packId
})

const fileInputRef = ref(null)
const assetKind = ref('token')
const targetW = ref(35)
const targetH = ref(35)
const assetName = ref('')
const category = ref('')
const packName = ref('')
const gameType = ref('fantasy')
const selectedFile = ref(null)
const previewImage = ref(null)
const uploading = ref(false)
const availablePacks = ref([])
const categories = ref([])

function applyKindDimensions() {
  const o = assetKindOptions.find((x) => x.value === assetKind.value)
  if (o) {
    targetW.value = o.w
    targetH.value = o.h
  }
}

function applyKindFromOption(opt) {
  assetKind.value = opt.value
  applyKindDimensions()
}

watch(assetKind, applyKindDimensions)

const loadPacks = async () => {
  try {
    const response = await api.getPacks()
    if (response.data) {
      availablePacks.value = response.data
    }
  } catch (error) {
    console.error('Error loading packs:', error)
  }
}

const loadPackCategories = async () => {
  if (!packName.value) {
    categories.value = []
    category.value = ''
    return
  }

  try {
    const response = await api.getPackAssets(packName.value)
    if (response.data) {
      categories.value = Object.keys(response.data)
      if (categories.value.length > 0) {
        category.value = categories.value[0]
      }
    }
  } catch (error) {
    console.error('Error loading pack categories:', error)
    categories.value = []
  }
}

function suggestKindForCategory(cat) {
  if (!cat) return
  if (cat.includes('01.tiles') || cat === '01.tiles') {
    assetKind.value = 'tile'
  } else if (cat.includes('05.') || cat.toLowerCase().includes('zombie') || cat.toLowerCase().includes('figure')) {
    assetKind.value = 'character'
  } else if (cat.toLowerCase().includes('spawn') || cat.toLowerCase().includes('pop')) {
    assetKind.value = 'pop'
  } else {
    assetKind.value = 'token'
  }
  applyKindDimensions()
}

const syncContextualFields = () => {
  if (props.show && isContextual.value) {
    packName.value = props.packId
    category.value = props.categoryPreset
    suggestKindForCategory(props.categoryPreset)
    gameType.value = getPackGameType(packName.value, loadPackGameTypeMap())
  }
}

watch(
  () => [props.show, props.packId, props.categoryPreset],
  () => {
    syncContextualFields()
  },
  { immediate: true }
)

function clampDim(n, fallback) {
  const v = Number(n)
  if (!Number.isFinite(v)) return fallback
  return Math.min(2048, Math.max(8, Math.round(v)))
}

const targetDimensions = computed(() => ({
  w: clampDim(targetW.value, 35),
  h: clampDim(targetH.value, 35)
}))

onMounted(async () => {
  await loadPacks()
  syncContextualFields()
  if (!isContextual.value) {
    applyKindDimensions()
  }
})

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const uploadAsset = async () => {
  if (!selectedFile.value) {
    alert('Veuillez sélectionner un fichier')
    return
  }

  if (!packName.value || !category.value) {
    alert('Veuillez sélectionner un pack et une catégorie')
    return
  }

  uploading.value = true

  try {
    const { w, h } = targetDimensions.value
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('asset_name', assetName.value)
    formData.append('target_width', String(w))
    formData.append('target_height', String(h))
    formData.append('category', category.value)
    formData.append('pack_name', packName.value)
    formData.append('game_type', gameType.value)

    await api.uploadCustomPack(formData)
    alert('Asset uploadé avec succès!')

    const pid = packName.value

    // Persister l'association pack -> type de jeu côté navigateur
    const map = loadPackGameTypeMap()
    map[pid] = gameType.value || map[pid] || 'fantasy'
    savePackGameTypeMap(map)

    emit('uploaded', { packId: pid })
    window.dispatchEvent(new CustomEvent('pack-assets-updated', { detail: { packId: pid } }))
    window.dispatchEvent(new CustomEvent('pack-game-type-updated', { detail: { packId: pid } }))

    assetName.value = ''
    assetKind.value = 'token'
    targetW.value = 35
    targetH.value = 35
    selectedFile.value = null
    previewImage.value = null
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }

    if (!isContextual.value) {
      category.value = ''
    } else {
      suggestKindForCategory(props.categoryPreset)
    }

    await loadPacks()
    window.dispatchEvent(new CustomEvent('packs-refresh'))
  } catch (error) {
    console.error('Error uploading asset:', error)
    alert("Erreur lors de l'upload: " + (error.response?.data?.error || error.message))
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.pack-uploader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.pack-uploader {
  padding: 20px;
  background: linear-gradient(135deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  border-radius: 8px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  color: white;
  border: 2px solid var(--primary-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--primary-color);
}

.modal-header h3 {
  margin: 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: white;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--primary-color);
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.hint {
  margin: 4px 0 0;
  font-size: 0.8rem;
  opacity: 0.85;
  line-height: 1.35;
}

.full-width {
  width: 100%;
}

.contextual-info .readonly-field {
  margin: 0;
  padding: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  border: 1px solid var(--brown-light);
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.95rem;
}

.form-group label {
  font-weight: 500;
  color: white;
}

.form-group input,
.form-group select {
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--primary-color);
}

.form-group select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.preview {
  margin-top: 10px;
}

.preview img {
  max-width: 200px;
  max-height: 200px;
  border: 2px solid var(--brown-light);
  border-radius: 4px;
}

.submit-btn {
  padding: 10px 20px;
  background: var(--brown-medium);
  color: white;
  border: 2px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  font-weight: 500;
}

.submit-btn:hover:not(:disabled) {
  background: var(--brown-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px var(--shadow-accent);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dim-inputs {
  display: flex;
  gap: 12px;
  margin-top: 4px;
}

.dim-inputs > div {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preset-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.preset-hint {
  font-size: 0.65rem;
  opacity: 0.55;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-right: 2px;
}

.preset-chip {
  font-size: 0.65rem;
  line-height: 1.2;
  padding: 3px 7px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.preset-chip:hover {
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.12);
}

.preset-chip.active {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 22%, transparent);
}
</style>
