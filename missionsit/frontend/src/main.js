// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import './setup'
import { createApp } from 'vue'
import { FrappeUI } from 'frappe-ui'
import '@fontsource-variable/bricolage-grotesque'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).use(router).use(FrappeUI).mount('#app')
