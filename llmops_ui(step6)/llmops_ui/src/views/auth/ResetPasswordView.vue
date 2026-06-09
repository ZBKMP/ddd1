<script setup lang="ts">
import Banner from './components/Banner.vue'
import ResetPasswordForm from './components/ResetPasswordForm.vue'
</script>

<template>
  <div class="flex h-screen bg-white">
    <div class="fixed top-6 left-[22px] inline-flex items-center">
      <div class="bg-gray-100 h-8 leading-8 px-2 z-50">博瑞LLMOps AppBuilder</div>
    </div>
    <banner />
    <div class="relative flex flex-1 items-center justify-center pb-10">
      <reset-password-form />
      <div class="absolute right-0 bottom-0 w-full">
        <footer class="flex items-center justify-center h-10 text-gray-600 text-center">
          博瑞LLMOps AppBuilder
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
