import { createApp } from 'vue'
import './style.css'
import 'flowbite'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router).mount('#app')

// ダークモード対応
function setDarkMode() {
  if (
    localStorage.getItem('color-theme') === 'dark' ||
    (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
  ) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}
setDarkMode()

const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)')
darkModeQuery.addEventListener('change', setDarkMode)
