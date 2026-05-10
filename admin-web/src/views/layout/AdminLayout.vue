<template>
  <div class="admin-shell">
    <AdminSidebar />
    <div class="admin-shell__main">
      <AdminTopBar />
      <main class="admin-shell__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import AdminSidebar from '../../components/layout/AdminSidebar.vue'
import AdminTopBar from '../../components/layout/AdminTopBar.vue'
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
  background: var(--bg-elevated);
}

.admin-shell__main {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-shell__content {
  flex: 1;
  padding: var(--sp-6);
}
</style>
