<template>
  <q-layout view="lHh Lpr lFf">

    <q-page-container>
      <q-toggle :model-value="isDarkMode" @update:model-value="toggleTheme" />
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { ref } from 'vue'

const $q = useQuasar()
const isDarkMode = ref($q.dark.isActive)

function toggleTheme(value: boolean) {
  isDarkMode.value = value
  $q.dark.set(value)
}
</script>
