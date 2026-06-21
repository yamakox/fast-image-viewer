<script setup lang="ts">
</script>

<template>
  <div class="login-page-container">
    <div class="text-heading text-xl mb-5">Fast Image Viewer</div>
    <form class="max-w-sm mx-auto">
      <div class="mb-5">
        <label for="username" class="block mb-2.5 text-sm font-medium text-heading">ユーザー名:</label>
        <input type="username" id="username" class="bg-neutral-secondary-medium border border-default-medium text-heading text-sm rounded-base focus:ring-brand focus:border-brand block w-full px-3 py-2.5 shadow-xs" required />
      </div>
      <div class="mb-5">
        <label for="password" class="block mb-2.5 text-sm font-medium text-heading">パスワード:</label>
        <input type="password" id="password" class="bg-neutral-secondary-medium border border-default-medium text-heading text-sm rounded-base focus:ring-brand focus:border-brand block w-full px-3 py-2.5 shadow-xs" required />
      </div>
      <button type="submit" class="text-white bg-brand box-border border border-transparent hover:bg-brand-strong focus:ring-4 focus:ring-brand-medium shadow-xs font-medium leading-5 rounded-base text-sm px-4 py-2.5 focus:outline-none">ログイン</button>
    </form>
  </div>
</template>

<style scoped>
.login-page-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
