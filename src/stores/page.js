import { defineStore } from 'pinia'
import { ref } from 'vue'

export const pageStore = defineStore('page', {
  state: () => ({
    current_page: null,
    page_key: 0,
  }),

  actions: {
    initPage(page_name) {
      this.current_page = page_name
      this.page_key = 0
    },
    changePage(page_name) {
      this.current_page = page_name
      this.page_key++
    },
    refreshCurrentPage() {
      this.page_key++
    }
  }
})