<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed } from 'vue'
import ChurchMap from '@/components/ChurchMap.vue'
import ChurchSubmit from '@/components/ChurchSubmit.vue'
import { directory, loadDirectory } from '@/data'

loadDirectory()

const churches = computed(() => directory.data?.churches || [])
</script>

<template>
  <div class="page pt-12">
    <h1 class="heading t-h1">Church Directory</h1>
    <p class="t-lead mt-3 max-w-2xl text-ink-soft">
      Churches that welcome missionaries, kept up to date by the people who know them. The map shows each church’s name and where it meets.
    </p>
    <p v-if="directory.data" class="mt-2 font-medium text-airmail">
      {{ churches.length === 1 ? '1 church on the map' : `${churches.length} churches on the map` }}
    </p>

    <ChurchMap class="mt-8" :churches="churches" height="min(32rem, 70vh)" />

    <ChurchSubmit class="mt-12" />
  </div>
</template>
