<template>
  <v-layout>
    <v-app-bar density="compact" title="SPSS Results Reader">
      <v-btn
        v-for="group in groups"
        :key="group.name"
        :text="group.name"
        append-icon="mdi-chevron-down"
        @focus="activate($event, group)"
        @mouseenter="activate($event, group)"
        @mouseleave="delayedClose()"
      ></v-btn>
    </v-app-bar>

    <v-menu
      v-model="menu"
      :activator="activator"
      :content-class="{ 'menu-move-transition': menuMoving }"
      location="bottom end"
      offset="4"
      viewport-margin="0"
    >
      <v-list
        :items="menuItems"
        class="py-1"
        density="compact"
        rounded="lg"
        border
        @mouseenter="onListEnter()"
        @mouseleave="delayedClose()"
        @click:select="handleSelect"
      >
      </v-list>
    </v-menu>

    <v-main>
      <div class="content">
        <component :is="pages[store.current_page]" :key="store.page_key"/>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { pageStore } from '@/stores/page'
const store = pageStore()

import Guide from './components/Guide.vue'
// Data
import Factor from './components/Data/Factor.vue'
import UserData from './components/Data/UserData.vue'
import SPSSExport from './components/Data/SPSSExport.vue'
// Project
import NewProject from './components/Project/NewProject.vue'
import OpenRecent from './components/Project/OpenRecent.vue'

const pages = {
  guide: Guide,
  // Data
  factor: Factor,
  user_data: UserData,
  spss_export: SPSSExport,
  // Project
  new_project: NewProject,
  open_recent: OpenRecent,
}
store.initPage('guide')

const groups = ref([
  {
    name: 'Home',
    items: [
      {
        title: 'Guide',
        value: 'guide'
      }
    ]
  },
  {
    name: 'Data',
    items: [
      {
        title: 'Factor',
        value: 'factor'
      },
      {
        title: 'User Data',
        value: 'user_data'
      },
      {
        title: 'SPSS Export',
        value: 'spss_export'
      }
    ]
  },
  {
    name: 'Project',
    items: [
      {
        title: 'New Project',
        value: 'new_project'
      },
      {
        title: 'Open Recent',
        value: 'open_recent'
      }
    ]
  }
])

const menu = ref(false)
const activator = ref(null)
const menuItems = ref([])
const menuMoving = ref(false)
let closeTimer = null

function activate(event, group) {
  clearTimeout(closeTimer)
  activator.value = event.currentTarget
  menuItems.value = group.items
  menu.value = true
}

function delayedClose() {
  closeTimer = setTimeout(() => {
    menu.value = false
  }, 200)
}

function onListEnter() {
  clearTimeout(closeTimer)
}

function handleSelect({ id }) {
  if (id === store.current_page) {
    store.refreshCurrentPage()
  }
  else {
    store.changePage(id)
  }
}
</script>

<style>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.toolbar {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #2c2c2c;
  color: white;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}
</style>