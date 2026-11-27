<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { watchEffect } from 'vue'
import { FrappeUIProvider } from 'frappe-ui'
import TopBar from '@/components/TopBar.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import { site } from '@/data'

watchEffect(() => {
  if (site.data?.title) document.title = site.data.title
})
</script>

<template>
  <FrappeUIProvider>
    <a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-30 focus:rounded focus:bg-white focus:px-3 focus:py-2">
      Skip to content
    </a>
    <TopBar />
    <main id="main" class="min-h-[60vh]">
      <RouterView />
    </main>
    <SiteFooter />
  </FrappeUIProvider>
</template>
