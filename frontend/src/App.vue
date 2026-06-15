<script setup>
import AppShell from "./components/AppShell.vue"
</script>

<template>
  <AppShell>
    <template #header>
      <RouterLink class="brand" to="/">ElectroLibrary</RouterLink>
      <nav>
        <RouterLink to="/">Книги</RouterLink>
        <RouterLink to="/references">Справочники</RouterLink>
      </nav>
    </template>

    <RouterView />
  </AppShell>
</template>
