import { createApp } from "vue"
import { createRouter, createWebHistory } from "vue-router"
import App from "./App.vue"
import BookFormView from "./views/BookFormView.vue"
import BooksView from "./views/BooksView.vue"
import ReferencesView from "./views/ReferencesView.vue"
import "./style.css"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: BooksView },
    { path: "/books/new", component: BookFormView },
    { path: "/books/:id/edit", component: BookFormView },
    { path: "/references", component: ReferencesView }
  ]
})

createApp(App).use(router).mount("#app")
