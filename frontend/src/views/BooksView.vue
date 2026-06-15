<script setup>
import { onMounted, reactive, ref } from "vue"
import { deleteBook, listBooks, listReferences } from "../api"
import MessageBox from "../components/MessageBox.vue"

const books = ref([])
const authors = ref([])
const genres = ref([])
const publishers = ref([])
const bookmark = ref(null)
const currentBookmark = ref(null)
const hasMore = ref(false)
const history = ref([])
const loading = ref(false)
const error = ref("")

const filters = reactive({
  search: "",
  author_id: "",
  genre_id: "",
  publisher_id: "",
  year: "",
  sort: "title",
  order: "asc",
  limit: "10"
})

async function loadBooks(nextBookmark = null, saveHistory = false) {
  loading.value = true
  error.value = ""
  try {
    if (saveHistory) {
      history.value.push(currentBookmark.value)
    }
    const data = await listBooks({ ...filters, bookmark: nextBookmark })
    books.value = data.items
    currentBookmark.value = nextBookmark
    bookmark.value = data.bookmark
    hasMore.value = data.has_more
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  history.value = []
  bookmark.value = null
  currentBookmark.value = null
  loadBooks()
}

function previousPage() {
  const previous = history.value.pop()
  loadBooks(previous)
}

async function removeBook(book) {
  if (!confirm(`Удалить книгу «${book.title}»?`)) return
  try {
    await deleteBook(book.id)
    await loadBooks(currentBookmark.value)
  } catch (err) {
    error.value = err.message
  }
}

onMounted(async () => {
  try {
    ;[authors.value, genres.value, publishers.value] = await Promise.all([
      listReferences("authors"),
      listReferences("genres"),
      listReferences("publishers")
    ])
    await loadBooks()
  } catch (err) {
    error.value = err.message
  }
})
</script>

<template>
  <section class="page-title">
    <div>
      <p class="eyebrow">Коллекция</p>
      <h1>Книги</h1>
    </div>
    <RouterLink class="button button-primary" to="/books/new">Добавить книгу</RouterLink>
  </section>

  <form class="panel filters" @submit.prevent="applyFilters">
    <label>
      Поиск
      <input v-model="filters.search" placeholder="Название книги">
    </label>
    <label>
      Автор
      <select v-model="filters.author_id">
        <option value="">Все авторы</option>
        <option v-for="item in authors" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <label>
      Жанр
      <select v-model="filters.genre_id">
        <option value="">Все жанры</option>
        <option v-for="item in genres" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <label>
      Издательство
      <select v-model="filters.publisher_id">
        <option value="">Все издательства</option>
        <option v-for="item in publishers" :key="item.id" :value="item.id">{{ item.name }}</option>
      </select>
    </label>
    <label>
      Год
      <input v-model="filters.year" type="number" min="1000" placeholder="Любой">
    </label>
    <label>
      Сортировка
      <select v-model="filters.sort">
        <option value="title">По названию</option>
        <option value="publication_year">По году</option>
      </select>
    </label>
    <label>
      Порядок
      <select v-model="filters.order">
        <option value="asc">По возрастанию</option>
        <option value="desc">По убыванию</option>
      </select>
    </label>
    <button class="button button-secondary">Применить</button>
  </form>

  <MessageBox v-if="error">{{ error }}</MessageBox>

  <div class="panel table-wrap">
    <table>
      <thead>
        <tr>
          <th>Название</th>
          <th>Автор</th>
          <th>Жанр</th>
          <th>Издательство</th>
          <th>Год</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td class="book-title">{{ book.title }}</td>
          <td>{{ book.author.name }}</td>
          <td>{{ book.genre.name }}</td>
          <td>{{ book.publisher.name }}</td>
          <td>{{ book.publication_year }}</td>
          <td class="actions">
            <RouterLink class="text-button" :to="`/books/${encodeURIComponent(book.id)}/edit`">Изменить</RouterLink>
            <button class="text-button danger" @click="removeBook(book)">Удалить</button>
          </td>
        </tr>
        <tr v-if="!books.length && !loading">
          <td class="empty" colspan="6">Книги не найдены</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="pagination">
    <button class="button button-secondary" :disabled="!history.length || loading" @click="previousPage">Назад</button>
    <span v-if="loading">Загрузка...</span>
    <button class="button button-secondary" :disabled="!hasMore || loading" @click="loadBooks(bookmark, true)">Далее</button>
  </div>
</template>
