<template>
  <div class="user_data">
    <ExcelFileHandler
      table_name="user_data"
      title="User Data"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import ExcelFileHandler from '@/components/Props/Data/ExcelFileHandler.vue';
</script>