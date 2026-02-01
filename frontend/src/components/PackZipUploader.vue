<template>
  <div v-if="show" class="pack-zip-uploader-overlay" @click.self="close">
    <div class="pack-zip-uploader">
    <div class="modal-header">
      <h3>Upload de Pack ZIP</h3>
      <button @click="close" class="close-btn">×</button>
    </div>
    <form @submit.prevent="uploadZip" class="upload-form">
      <div class="form-group">
        <label>Fichier ZIP</label>
        <input type="file" @change="handleFileSelect" accept=".zip" required />
        <div v-if="zipFileName" class="file-info">
          Fichier sélectionné: {{ zipFileName }}
        </div>
      </div>
      
      <div class="form-group">
        <label>
          <input v-model="replaceExisting" type="checkbox" />
          Remplacer si existe déjà
        </label>
      </div>
      
      <div v-if="uploadProgress" class="progress">
        <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
        <span>{{ uploadProgress }}%</span>
      </div>
      
      <button type="submit" :disabled="uploading" class="submit-btn">
        {{ uploading ? 'Upload en cours...' : 'Upload et Extraire' }}
      </button>
    </form>
    
    <div v-if="uploadedPacks.length > 0" class="uploaded-packs">
      <h4>Packs uploadés récemment</h4>
      <ul>
        <li v-for="pack in uploadedPacks" :key="pack.id">
          <span class="pack-name">{{ pack.name }}</span>
          <button @click="deletePack(pack.id)" class="delete-btn">Supprimer</button>
        </li>
      </ul>
    </div>
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

const selectedFile = ref(null)
const zipFileName = ref('')
const replaceExisting = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedPacks = ref([])

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    zipFileName.value = file.name
  }
}

const uploadZip = async () => {
  if (!selectedFile.value) {
    alert('Veuillez sélectionner un fichier ZIP')
    return
  }
  
  uploading.value = true
  uploadProgress.value = 0
  
  try {
    const formData = new FormData()
    formData.append('zip_file', selectedFile.value)
    formData.append('replace_existing', replaceExisting.value)
    
    // Simulate progress (in real app, use axios progress event)
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    const response = await api.uploadPackZip(formData)
    uploadProgress.value = 100
    
    clearInterval(progressInterval)
    alert('Pack uploadé avec succès!')
    
    // Reset and reload packs
    selectedFile.value = null
    zipFileName.value = ''
    uploadProgress.value = 0
    loadUploadedPacks()
    
    // Reload packs in AssetPanel (trigger refresh)
    window.dispatchEvent(new CustomEvent('packs-refresh'))
  } catch (error) {
    console.error('Error uploading ZIP:', error)
    alert('Erreur lors de l\'upload: ' + (error.response?.data?.error || error.message))
    uploadProgress.value = 0
  } finally {
    uploading.value = false
  }
}

const loadUploadedPacks = async () => {
  try {
    const response = await api.getUploadedPacks()
    uploadedPacks.value = response.data || []
  } catch (error) {
    console.error('Error loading uploaded packs:', error)
  }
}

const deletePack = async (packId) => {
  if (!confirm(`Supprimer le pack ${packId}?`)) {
    return
  }
  
  try {
    await api.delete(`/packs/uploaded/${packId}/`)
    loadUploadedPacks()
    alert('Pack supprimé')
  } catch (error) {
    console.error('Error deleting pack:', error)
    alert('Erreur lors de la suppression')
  }
}

onMounted(() => {
  loadUploadedPacks()
})
</script>

<style scoped>
.pack-zip-uploader-overlay {
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

.pack-zip-uploader {
  padding: 20px;
  background: linear-gradient(135deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  border-radius: 8px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  color: white;
  border: 2px solid var(--primary-color);
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

.form-group input[type="file"],
.form-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.file-info {
  font-size: 0.9rem;
  color: #666;
}

.progress {
  position: relative;
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #457b9d;
  transition: width 0.3s;
}

.progress span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.8rem;
  color: white;
  font-weight: 500;
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

.uploaded-packs {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid var(--primary-color);
}

.uploaded-packs h4 {
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
  margin-bottom: 10px;
}

.uploaded-packs ul {
  list-style: none;
  padding: 0;
}

.uploaded-packs li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.uploaded-packs .pack-name {
  color: white;
  font-weight: 500;
}

.delete-btn {
  padding: 4px 8px;
  background: #e63946;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  background: #bc1c1c;
}
</style>
