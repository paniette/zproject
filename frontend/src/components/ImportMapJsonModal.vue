<template>
  <div v-if="show" class="overlay" @click.self="emit('close')">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="import-map-title">
      <div class="modal-header">
        <h3 id="import-map-title">{{ $t('importModal.title') }}</h3>
        <button type="button" class="close-btn" :aria-label="$t('common.close')" @click="emit('close')">×</button>
      </div>

      <div class="modal-body">
        <p class="hint">{{ $t('importModal.hint') }}</p>

        <label for="import-json-textarea" class="label">{{ $t('importModal.label') }}</label>
        <textarea
          id="import-json-textarea"
          ref="textareaRef"
          v-model="jsonText"
          class="textarea"
          spellcheck="false"
          :placeholder="$t('importModal.placeholder')"
          @input="clearErrors"
        />

        <ul v-if="validationErrors.length" class="error-list">
          <li v-for="(err, i) in validationErrors" :key="i">{{ err }}</li>
        </ul>
        <p v-else-if="parseError" class="error">{{ parseError }}</p>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn secondary" @click="emit('close')">{{ $t('importModal.cancel') }}</button>
        <button type="button" class="btn primary" @click="submit">{{ $t('importModal.import') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  parseMapJsonText,
  getImportValidationErrors,
  MapImportError
} from '@/utils/mapImport'

const { t } = useI18n()

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'submit'])

const jsonText = ref('')
const parseError = ref('')
const validationErrors = ref([])
const textareaRef = ref(null)

watch(
  () => props.show,
  async (on) => {
    if (!on) return
    parseError.value = ''
    validationErrors.value = []
    await nextTick()
    textareaRef.value?.focus?.()
  },
  { immediate: true }
)

function clearErrors () {
  parseError.value = ''
  validationErrors.value = []
}

function validationMessages (codes) {
  return codes.map((code) => t(`importModal.errors.${code}`))
}

function submit () {
  parseError.value = ''
  validationErrors.value = []

  const raw = jsonText.value
  if (!raw.trim()) {
    parseError.value = t('importModal.errors.empty')
    return
  }

  let parsed
  try {
    parsed = parseMapJsonText(raw)
  } catch (e) {
    if (e instanceof MapImportError) {
      parseError.value = t('importModal.errors.invalidJson')
    } else {
      parseError.value = t('importModal.errors.invalidJson')
    }
    return
  }

  const codes = getImportValidationErrors(parsed)
  if (codes.length) {
    validationErrors.value = validationMessages(codes)
    return
  }

  emit('submit', parsed)
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
  max-width: 720px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
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
  flex-shrink: 0;
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
  overflow: hidden;
  flex: 1;
  min-height: 0;
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

.textarea {
  flex: 1;
  min-height: 280px;
  max-height: 50vh;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--brown-light);
  background: rgba(0, 0, 0, 0.25);
  color: #eee;
  font-family: ui-monospace, 'Cascadia Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.4;
  resize: vertical;
}

.textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(0, 0, 0, 0.35);
}

.error {
  margin: 0;
  color: #ffb4b4;
  font-size: 0.85rem;
}

.error-list {
  margin: 0;
  padding-left: 1.2rem;
  color: #ffb4b4;
  font-size: 0.85rem;
}

.error-list li {
  margin-bottom: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 16px 16px;
  flex-shrink: 0;
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
