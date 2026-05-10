<template>
  <TopBar @open-drawer="drawerOpen = true" />
  <main class="page-container">
    <router-view />
  </main>
  <SiteFooter />
  <MobileNavDrawer v-model:show="drawerOpen" />
</template>

<script setup>
import { ref } from 'vue'

import TopBar from './TopBar.vue'
import SiteFooter from './SiteFooter.vue'
import MobileNavDrawer from './MobileNavDrawer.vue'

const drawerOpen = ref(false)
</script>
