<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { postData } from '../util'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function handleSubmit(event: Event) {
  event.preventDefault()
  error.value = ''
  const { ok, result } = await postData('/api/v1/login', {
    username: username.value,
    password: password.value,
  })
  if (ok) {
    location.href = router.resolve({ name: 'Main' }).href
    return
  }
  error.value = (result?.detail as string) ?? 'ログインに失敗しました。'
}
</script>

<template>
  <div class="login-page-container">
    <div class="text-heading mb-5 text-xl">Fast Image Viewer</div>
    <form class="mx-auto max-w-sm" @submit="handleSubmit">
      <div class="mb-5">
        <label for="username" class="text-heading mb-2.5 block text-sm font-medium">ユーザー名:</label>
        <input
          v-model="username"
          type="text"
          id="username"
          class="bg-neutral-secondary-medium border-default-medium text-heading rounded-base focus:ring-brand focus:border-brand block w-full border px-3 py-2.5 text-sm shadow-xs"
          required
        />
      </div>
      <div class="mb-5">
        <label for="password" class="text-heading mb-2.5 block text-sm font-medium">パスワード:</label>
        <input
          v-model="password"
          type="password"
          id="password"
          class="bg-neutral-secondary-medium border-default-medium text-heading rounded-base focus:ring-brand focus:border-brand block w-full border px-3 py-2.5 text-sm shadow-xs"
          required
        />
      </div>
      <p v-if="error" class="mb-5 text-sm text-red-600">{{ error }}</p>
      <button
        type="submit"
        class="bg-brand hover:bg-brand-strong focus:ring-brand-medium rounded-base box-border border border-transparent px-4 py-2.5 text-sm leading-5 font-medium text-white shadow-xs focus:ring-4 focus:outline-none"
      >
        ログイン
      </button>
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
