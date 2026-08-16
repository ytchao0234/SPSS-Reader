<template>
  <div class="guide">
    <div v-if="readme" class="markdown-body" v-html="readme"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked'

const readme = ref('')
const loading = ref(true)

async function loadReadme() {
  const md = await window.api.readMe()
  const renderer = new marked.Renderer()

  renderer.heading = ({ tokens, depth }) => {
    const text = tokens.map(token => token.raw ?? '').join('')
    const id = text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')

    return `<h${depth} id="${id}">${text}</h${depth}>`
  }

  readme.value = marked.parse(md, { renderer })
  // const res = await window.api.checkForeignKey()
  // console.log(res)
}

onMounted(() => {
  loadReadme()
})
</script>