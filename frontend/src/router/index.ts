import {createRouter, createWebHistory} from 'vue-router'

const router = createRouter(
  {
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        component: () => import('@/views/mainEditorPage.vue')
      },
      {
        path: '/login',
        component: () => import('@/views/loginPage.vue')
      }
    ]
  }
)

export default router