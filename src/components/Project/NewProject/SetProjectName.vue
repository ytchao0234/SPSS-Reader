<template>
  <div class="set_project_name">
    <v-card class="pa-4" flat>
      <v-card-title>
        <div class="d-flex align-center ga-4">
          <h3 class="my-0">Set Project Name</h3>

          <IconTooltip
            type="info"
            location="bottom"
            :hint_message="utility.set_project_name_hint_msg"
          />
        </div>
      </v-card-title>

      <v-text-field v-model="store.project_name" label="Project Name"></v-text-field>
    </v-card>
  </div>
</template>

<script setup>
import { utilityStore } from '@/stores/utility'
import { newProjectStore } from '@/stores/newProject'
const utility = utilityStore()
const store = newProjectStore()

import IconTooltip from '@/components/Props/IconTooltip.vue'
</script>