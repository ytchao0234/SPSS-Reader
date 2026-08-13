import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const spssReaderStore = defineStore('spss_reader', () => {
    const project_id = ref(null)

    function reset() {
        project_id.value = null
    }

    return {
        reset,
        project_id
    }
})