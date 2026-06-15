<script setup>
defineProps({
  type: {
    type: String,
    default: "error"
  }
})
</script>

<template>
  <div class="message" :class="`message-${type}`">
    <slot />
  </div>
</template>
