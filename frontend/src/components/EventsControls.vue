<script setup lang="ts">
import { useQuasar } from 'quasar'
import { ref } from 'vue'
import type { FiltersData } from 'src/api/types'

defineProps<{ data: FiltersData }>()

const city = defineModel<string | undefined>('city', { required: true })
const date = defineModel<string | undefined>('date', { required: true })
const category = defineModel<string | undefined>('category', { required: true })

const $q = useQuasar()
const isDarkMode = ref($q.dark.isActive)

function toggleTheme(value: boolean) {
  isDarkMode.value = value
  $q.dark.set(value)
}

// function filterCities(val, update) {
  // if (val === '') {
  //   update(() => {
  //     filtersData.value.cities
  //   })
  //   return
  // }
  //
  // update(() => {
  //   const needle = val.toLowerCase()
  //   filtersData.value.cities = filtersData.value.cities.filter(v => v.name.toLowerCase().indexOf(needle) > -1)
  // })
// }
</script>

<template>
  <q-btn class="page__date" icon="event" round color="deep-orange">
    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
      <q-date v-model="date" today-btn mask="YYYY-MM-DD" color="deep-orange" />
    </q-popup-proxy>
  </q-btn>
  <q-select
    v-model="city"
    class="page__select"
    :options="data.cities"
    option-value="id"
    option-label="name"
    label="Выберите город"
    filled
    emit-value
    map-options
    clearable
    use-input
    input-debounce="0"
  >
    <template #prepend>
      <q-icon name="place" />
    </template>
    <template #no-option>
      <q-item>
        <q-item-section class="text-grey">Не найдено</q-item-section>
      </q-item>
    </template>
  </q-select>
  <q-select
    v-model="category"
    class="page__select"
    :options="data.categories"
    option-value="id"
    option-label="name"
    label="Выберите Категорию"
    filled
    emit-value
    map-options
    clearable
    use-input
    input-debounce="0"
  >
    <template #no-option>
      <q-item>
        <q-item-section class="text-grey">Не найдено</q-item-section>
      </q-item>
    </template>
  </q-select>
  <q-toggle
    size="lg"
    color="blue"
    checked-icon="dark_mode"
    unchecked-icon="light_mode"
    :model-value="isDarkMode"
    @update:model-value="toggleTheme"
  />
</template>

<style scoped lang="scss"></style>
