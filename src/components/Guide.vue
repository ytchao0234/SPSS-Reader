<template>
  <div class="guide">
    <div v-if="readme" v-html="readme"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked'

const readme = ref('')
const loading = ref(true)

async function loadReadme() {
  const md = await window.api.readMe()
  readme.value = marked.parse(md)
  // const res = await window.api.checkForeignKey()
  // console.log(res)
}

onMounted(() => {
  loadReadme()
})
</script>