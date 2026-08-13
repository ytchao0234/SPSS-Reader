<template>
  <div class="spss_export">
    <ExcelFileHandler
      table_name="spss_export"
      title="SPSS Export"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { utilityStore } from '@/stores/utility'
const utility = utilityStore()

import ExcelFileHandler from '@/components/Props/Data/ExcelFileHandler.vue';
</script>