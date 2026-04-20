<template>
  <div v-if="show" class="overlay" @click.self="emit('close')">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="save-map-title">
      <div class="modal-header">
        <h3 id="save-map-title">Nom de la carte</h3>
        <button type="button" class="close-btn" aria-label="Fermer" @click="emit('close')">×</button>
      </div>

      <div class="modal-body">
        <p class="hint">
          Premier enregistrement : donne un nom à la carte.
        </p>

        <label for="map-name-input" class="label">Nom</label>
        <input
          id="map-name-input"
          ref="inputRef"
          v-model="localName"
          class="input"
          type="text"
          autocomplete="off"
          placeholder="ex. Ma mission 01"
          @keydown.enter.prevent="submit"
        />

        <p v-if="error" class="error">{{ error }}</p>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn secondary" @click="emit('close')">Annuler</button>
        <button type="button" class="btn primary" @click="submit">Enregistrer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  initialName: { type: String, default: '' }
})

const emit = defineEmits(['close', 'submit'])

const localName = ref('')
const error = ref('')
const inputRef = ref(null)

watch(
  () => props.show,
  async (on) => {
    if (!on) return
    error.value = ''
    localName.value = (props.initialName || '').trim()
    await nextTick()
    inputRef.value?.focus?.()
    inputRef.value?.select?.()
  },
  { immediate: true }
)

function submit () {
  const name = (localName.value || '').trim()
  if (!name) {
    error.value = 'Veuillez saisir un nom.'
    return
  }
  emit('submit', name)
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 2500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal {
  width: 100%;
  max-width: 520px;
  border-radius: 10px;
  border: 2px solid var(--primary-color);
  background: linear-gradient(135deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  color: #fff;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.55);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}

.modal-header h3 {
  margin: 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 14px 16px 6px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hint {
  margin: 0;
  opacity: 0.85;
  font-size: 0.9rem;
  line-height: 1.35;
}

.label {
  font-weight: 600;
  font-size: 0.85rem;
}

.input {
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--brown-light);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 14px;
}

.input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.12);
}

.error {
  margin: 0;
  color: #ffb4b4;
  font-size: 0.85rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 16px 16px;
}

.btn {
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--brown-light);
  background: var(--brown-medium);
  color: #fff;
  font-size: 14px;
}

.btn:hover {
  border-color: var(--primary-color);
}

.btn.primary {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 35%, var(--brown-medium));
}

.btn.secondary {
  background: rgba(255, 255, 255, 0.06);
}
</style>
