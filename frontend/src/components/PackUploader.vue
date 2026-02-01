<template>
  <div v-if="show" class="pack-uploader-overlay" @click.self="close">
    <div class="pack-uploader">
      <div class="modal-header">
        <h3>Upload d'Asset Personnalisé</h3>
        <button @click="close" class="close-btn">×</button>
      </div>
      <form @submit.prevent="uploadAsset" class="upload-form">
        <div class="form-group">
          <label>Fichier image</label>
          <input type="file" @change="handleFileSelect" accept="image/*" required />
          <div v-if="previewImage" class="preview">
            <img :src="previewImage" alt="Preview" />
          </div>
        </div>
        
        <div class="form-group">
          <label>Nom de l'asset</label>
          <input v-model="assetName" type="text" required />
        </div>
        
        <div class="form-group">
          <label>Taille cible (pixels)</label>
          <input v-model.number="targetSize" type="number" min="16" max="512" required />
        </div>
        
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
          <label>Catégorie</label>
          <select v-model="category" :disabled="!packName || categories.length === 0" required>
            <option value="">Sélectionner une catégorie</option>
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>
        
        <button type="submit" :disabled="uploading || !packName || !category" class="submit-btn">
          {{ uploading ? 'Upload en cours...' : 'Upload et Normaliser' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  show: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const assetName = ref('')
const targetSize = ref(250)
const category = ref('')
const packName = ref('')
const selectedFile = ref(null)
const previewImage = ref(null)
const uploading = ref(false)
const availablePacks = ref([])
const categories = ref([])

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

onMounted(async () => {
  await loadPacks()
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
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('asset_name', assetName.value)
    formData.append('target_size', targetSize.value)
    formData.append('category', category.value)
    formData.append('pack_name', packName.value)
    
    await api.uploadCustomPack(formData)
    alert('Asset uploadé avec succès!')
    
    // Reset form
    assetName.value = ''
    targetSize.value = 250
    selectedFile.value = null
    previewImage.value = null
    category.value = ''
    
    // Reload packs to refresh
    await loadPacks()
    // Trigger pack refresh in AssetPanel
    window.dispatchEvent(new CustomEvent('packs-refresh'))
  } catch (error) {
    console.error('Error uploading asset:', error)
    alert('Erreur lors de l\'upload: ' + (error.response?.data?.error || error.message))
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
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
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
  box-shadow: 0 2px 8px rgba(230, 57, 70, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
