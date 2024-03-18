<script setup lang="ts">
import { ref } from 'vue'
import type { FiltersData } from 'src/api/types'

defineProps<{ data: FiltersData }>()

const emit = defineEmits<{
  (e: 'search', value: string): void
  (e: 'clear'): void
}>()

const city = defineModel<string | undefined>('city', { required: true })
const category = defineModel<string | undefined>('category', { required: true })

const search = ref('')
</script>

<template>
  <div class="controls">
    <q-select
      v-model="city"
      class="controls__select"
      :options="data.cities"
      option-value="id"
      option-label="name"
      label="Выберите город"
      filled
      emit-value
      map-options
      clearable
    >
      <template #prepend>
        <q-icon name="place" />
      </template>
    </q-select>
    <q-input
      v-model="search"
      clearable
      filled
      label="Искать по названию"
      class="controls__search"
      @keyup.enter="emit('search', search)"
      @clear="emit('clear')"
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>
    <q-select
      v-model="category"
      class="controls__select"
      :options="data.categories"
      option-value="id"
      option-label="name"
      label="Выберите Категорию"
      filled
      emit-value
      map-options
      clearable
    />
  </div>
</template>

<style scoped lang="scss">
.controls {
  display: flex;
  justify-content: space-between;
  gap: 20px;

  &__search {
    flex: 1 1 auto;
  }

  &__select {
    flex-basis: 250px;
  }
}
</style>
