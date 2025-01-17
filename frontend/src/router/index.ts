import {createRouter, createWebHistory} from 'vue-router'

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

export default router