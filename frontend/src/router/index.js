import { createRouter, createWebHashHistory } from 'vue-router'
import EditorLayout from '@/components/EditorLayout.vue'

const routes = [
  {
    path: '/',
    name: 'MapEditor',
    component: EditorLayout
  },
  {
    path: '/mission',
    name: 'MissionEditor',
    component: EditorLayout
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router