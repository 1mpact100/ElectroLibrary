const API_URL = "/api/v1"

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options
  })

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail?.message || "Не удалось выполнить запрос")
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export function listBooks(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      search.set(key, value)
    }
  })
  return request(`/books?${search}`)
}

export function getBook(id) {
  return request(`/books/${encodeURIComponent(id)}`)
}

export function createBook(data) {
  return request("/books", { method: "POST", body: JSON.stringify(data) })
}

export function updateBook(id, data) {
  return request(`/books/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) })
}

export function deleteBook(id) {
  return request(`/books/${encodeURIComponent(id)}`, { method: "DELETE" })
}

export function listReferences(type) {
  return request(`/${type}`)
}

export function createReference(type, name) {
  return request(`/${type}`, { method: "POST", body: JSON.stringify({ name }) })
}

export function updateReference(type, id, name) {
  return request(`/${type}/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify({ name }) })
}

export function deleteReference(type, id) {
  return request(`/${type}/${encodeURIComponent(id)}`, { method: "DELETE" })
}
