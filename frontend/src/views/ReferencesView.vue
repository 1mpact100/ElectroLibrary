<script setup>
import { onMounted, reactive, ref } from "vue"
import { createReference, deleteReference, listReferences, updateReference } from "../api"
import MessageBox from "../components/MessageBox.vue"

const groups = [
  { type: "authors", title: "Авторы", placeholder: "Имя автора" },
  { type: "genres", title: "Жанры", placeholder: "Название жанра" },
  { type: "publishers", title: "Издательства", placeholder: "Название издательства" }
]

const items = reactive({ authors: [], genres: [], publishers: [] })
const names = reactive({ authors: "", genres: "", publishers: "" })
const error = ref("")

async function load(type) {
  items[type] = await listReferences(type)
}

async function add(type) {
  if (!names[type].trim()) return
  error.value = ""
  try {
    await createReference(type, names[type])
    names[type] = ""
    await load(type)
  } catch (err) {
    error.value = err.message
  }
}

async function rename(type, item) {
  const name = prompt("Новое название", item.name)
  if (!name || name === item.name) return
  error.value = ""
  try {
    await updateReference(type, item.id, name)
    await load(type)
  } catch (err) {
    error.value = err.message
  }
}

async function remove(type, item) {
  if (!confirm(`Удалить «${item.name}»?`)) return
  error.value = ""
  try {
    await deleteReference(type, item.id)
    await load(type)
  } catch (err) {
    error.value = err.message
  }
}

onMounted(async () => {
  try {
    await Promise.all(groups.map(({ type }) => load(type)))
  } catch (err) {
    error.value = err.message
  }
})
</script>

<template>
  <section class="page-title">
    <div>
      <p class="eyebrow">Связанные данные</p>
      <h1>Справочники</h1>
    </div>
  </section>

  <MessageBox v-if="error">{{ error }}</MessageBox>

  <div class="reference-grid">
    <section v-for="group in groups" :key="group.type" class="panel reference-card">
      <h2>{{ group.title }}</h2>
      <form class="inline-form" @submit.prevent="add(group.type)">
        <input v-model="names[group.type]" required maxlength="200" :placeholder="group.placeholder">
        <button class="button button-primary">Добавить</button>
      </form>
      <ul>
        <li v-for="item in items[group.type]" :key="item.id">
          <span>{{ item.name }}</span>
          <span class="actions">
            <button class="text-button" @click="rename(group.type, item)">Изменить</button>
            <button class="text-button danger" @click="remove(group.type, item)">Удалить</button>
          </span>
        </li>
        <li v-if="!items[group.type].length" class="empty">Пока пусто</li>
      </ul>
    </section>
  </div>
</template>
