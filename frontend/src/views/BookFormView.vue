<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { createBook, getBook, listReferences, updateBook } from "../api"
import MessageBox from "../components/MessageBox.vue"

const route = useRoute()
const router = useRouter()
const editing = computed(() => Boolean(route.params.id))
const authors = ref([])
const genres = ref([])
const publishers = ref([])
const error = ref("")
const saving = ref(false)

const form = reactive({
  title: "",
  publication_year: new Date().getFullYear(),
  author_id: "",
  genre_id: "",
  publisher_id: ""
})

async function save() {
  saving.value = true
  error.value = ""
  try {
    const data = { ...form, publication_year: Number(form.publication_year) }
    if (editing.value) {
      await updateBook(route.params.id, data)
    } else {
      await createBook(data)
    }
    router.push("/")
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    ;[authors.value, genres.value, publishers.value] = await Promise.all([
      listReferences("authors"),
      listReferences("genres"),
      listReferences("publishers")
    ])
    if (editing.value) {
      const book = await getBook(route.params.id)
      Object.assign(form, {
        title: book.title,
        publication_year: book.publication_year,
        author_id: book.author.id,
        genre_id: book.genre.id,
        publisher_id: book.publisher.id
      })
    }
  } catch (err) {
    error.value = err.message
  }
})
</script>

<template>
  <section class="page-title">
    <div>
      <p class="eyebrow">{{ editing ? "Редактирование" : "Новая запись" }}</p>
      <h1>{{ editing ? "Изменить книгу" : "Добавить книгу" }}</h1>
    </div>
  </section>

  <MessageBox v-if="error">{{ error }}</MessageBox>
  <MessageBox v-if="!authors.length || !genres.length || !publishers.length" type="info">
    Для создания книги сначала добавьте автора, жанр и издательство в справочниках.
  </MessageBox>

  <form class="panel book-form" @submit.prevent="save">
    <label>
      Название
      <input v-model="form.title" required maxlength="300">
    </label>
    <label>
      Год издания
      <input v-model="form.publication_year" required type="number" min="1000" :max="new Date().getFullYear()">
    </label>
    <label>
      Автор
      <select v-model="form.author_id" required>
        <option disabled value="">Выберите автора</option>
        <option v-for="item in authors" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <label>
      Жанр
      <select v-model="form.genre_id" required>
        <option disabled value="">Выберите жанр</option>
        <option v-for="item in genres" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <label>
      Издательство
      <select v-model="form.publisher_id" required>
        <option disabled value="">Выберите издательство</option>
        <option v-for="item in publishers" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <div class="form-actions">
      <RouterLink class="button button-secondary" to="/">Отмена</RouterLink>
      <button class="button button-primary" :disabled="saving">{{ saving ? "Сохранение..." : "Сохранить" }}</button>
    </div>
  </form>
</template>
