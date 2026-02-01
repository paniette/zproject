import { createRouter, createWebHistory } from 'vue-router'
import MapEditor from '@/components/MapEditor.vue'

const routes = [
  {
    path: '/',
    name: 'MapEditor',
    component: MapEditor
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
