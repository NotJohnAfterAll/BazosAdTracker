import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './assets/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)

// Mount app
app.mount('#app')
