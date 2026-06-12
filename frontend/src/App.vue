<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <RouterView class="router-view" />
  </div>
</template>

<style scoped>
.app-container {
  margin: 0;
  padding: 0;
}

.router-view {
  margin: 0;
  padding: 0;
}
</style>
