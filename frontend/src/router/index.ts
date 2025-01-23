import {createRouter, createWebHistory} from 'vue-router'
import { editingState } from '@/components/NodeEditorStore'

const router = createRouter(
  {
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        redirect: '/edit'
      },
      {
        path: '/login',
        component: () => import('@/views/LoginPage.vue')
      },
      {
        path: '/edit',
        component: () => import('@/views/MainEditorPage.vue')
      },
      {
        path: '/edit/:datasetName/:itemName',
        component: () => import('@/views/MainEditorPage.vue')
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
      }    
    ]
  }
)

router.beforeEach((_to, from) => {
  if(from.path.startsWith('/edit') && !editingState.saved) {
    const confirmResult = confirm('You have unsaved changes. Are you sure you want to leave?')
    if(confirmResult) {
      return true
    }
    return false
  }
  return true
})

router.afterEach((_to, _from) => {
  editingState.saved = true
})

export default router