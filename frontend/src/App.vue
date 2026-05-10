<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-loading-bar-provider>
          <AppShell />
        </n-loading-bar-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {
  NConfigProvider,
  NDialogProvider,
  NLoadingBarProvider,
  NMessageProvider
} from 'naive-ui'

import AppShell from './components/layout/AppShell.vue'

const themeOverrides = {
  common: {
    primaryColor: '#b3261e',
    primaryColorHover: '#8e1c17',
    primaryColorPressed: '#7a1812',
    primaryColorSuppl: '#b3261e',
    borderRadius: '8px',
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
  }
}
</script>
