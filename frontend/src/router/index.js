import { createRouter, createWebHashHistory } from 'vue-router'
import MapEditor from '@/components/MapEditor.vue'

const routes = [
  {
    path: '/',
    name: 'MapEditor',
    component: MapEditor
  }
]

const router = createRouter({
  history: createWebHashHistory(),  // HashHistory fonctionne mieux avec les fichiers statiques
  routes
})

export default router
