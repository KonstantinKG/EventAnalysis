<script setup lang="ts">
import EventAnalysisService from 'src/api'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { EventData } from 'src/api/types'

const router = useRouter()
const route = useRoute()

const id = computed<string>(() => route.params.id)
const event = ref<EventData>()

async function getEvent() {
  try {
    const { data } = await EventAnalysisService.getById(id.value)
    event.value = data
  } catch (e) {
    console.error(e)
  }
}
getEvent()
</script>

<template>
  <q-btn @click="router.back()">Назад</q-btn>
  <div>
    <pre>{{ event }}</pre>
  </div>
</template>

<style scoped lang="scss"></style>
