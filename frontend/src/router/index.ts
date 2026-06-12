import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../pages/MainPage.vue'

const router = createRouter({
  // NOTE: BASE_URLの値はvite.config.tsの`base`の値に依存する。
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Main',
      component: MainPage,
    },
  ],
})

export default router
