<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { site } from '@/data'
</script>

<template>
  <footer class="mt-24 bg-ink text-white/80">
    <div class="page grid gap-10 py-14 md:grid-cols-[2fr_1fr_1fr]">
      <div>
        <p class="heading t-h3 text-white">{{ site.data?.title || 'Missions' }}</p>
        <p class="mt-3 max-w-sm text-sm leading-6">
          {{ site.data?.footer || 'Sending missionaries, and the people who stand behind them.' }}
        </p>
      </div>
      <nav aria-label="Footer" class="grid content-start gap-2 text-sm">
        <RouterLink to="/missionaries" class="hover:text-white">Missionaries</RouterLink>
        <RouterLink to="/trips" class="hover:text-white">Trips</RouterLink>
        <RouterLink to="/give" class="hover:text-white">Give</RouterLink>
        <RouterLink to="/portal" class="hover:text-white">Member Portal</RouterLink>
      </nav>
      <p class="text-sm leading-6 text-white/60">
        "Go ye into all the world, and preach the gospel to every creature."
        <span class="block">Mark 16:15</span>
      </p>
    </div>
  </footer>
</template>
