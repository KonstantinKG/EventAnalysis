<template>
  <!--  <q-page padding class="page">-->
  <div class="page">
    <div class="page__controls">
      <q-btn class="page_date" icon="event" round color="deep-orange">
        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
          <q-date
            v-model="date"
            today-btn
            mask="YYYY-MM-DD"
            color="deep-orange"
            :events="filtersData.dates"
            :options="optionsFn"
          />
        </q-popup-proxy>
      </q-btn>
      <q-select
        v-model="city"
        class="page__select"
        filled
        :options="filtersData.cities"
        option-value="id"
        option-label="name"
        label="Выберите город"
        emit-value
        map-options
        clearable
      />
    </div>
    <div class="page__cards">
      <q-card
        v-for="event in eventsData.events"
        :key="event.id"
        class="page__card"
      >
        <q-img
          :src="event.photo"
          :alt="`Картинка - ${event.title}`"
          fit="cover"
        >
          <div class="absolute-bottom">
            {{ event.category.name }}
          </div>
        </q-img>
        <q-card-section>
          {{ event.title }}
        </q-card-section>
        <q-card-section>
          {{ event.description }}
        </q-card-section>
        <q-card-section>
          {{ event.city.name }} {{ event.category.name }} {{ event.start }}
          {{ event.end }}
        </q-card-section>
      </q-card>
    </div>
    <q-btn
      v-if="eventsData.current < eventsData.pages"
      :loading="isLoadingMore"
      outline
      padding="md xl"
      class="page__btn"
      color="deep-orange"
      size="1.15rem"
      @click="loadMore"
    >
      Показать еще
    </q-btn>
  </div>
  <!--  </q-page>-->
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { AllEventsData, FiltersData } from 'src/api/types'
import EventAnalysisService from 'src/api'

const eventsData = ref<AllEventsData>({
  current: 1,
  pages: 1,
  events: [],
})
const page = ref(1)
const date = ref<string>()
const city = ref<string>()
const category = ref<string>()
const isLoading = ref(false)
const isLoadingMore = ref(false)

async function getAllEvents(loadMore = false) {
  try {
    if (!loadMore) isLoading.value = true
    const { data } = await EventAnalysisService.getAll({
      page: page.value,
      category_id: category.value,
      city_id: city.value,
      date: date.value,
    })
    if (data.current > 1) {
      eventsData.value.current = data.current
      eventsData.value.events = eventsData.value.events.concat(data.events)
    } else {
      eventsData.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

getAllEvents()

async function loadMore() {
  isLoadingMore.value = true
  page.value++
  await getAllEvents(true)
  isLoadingMore.value = false
}

const filtersData = ref<FiltersData>({
  categories: [],
  cities: [],
  dates: [],
})

async function getFilters() {
  try {
    const { data } = await EventAnalysisService.getFilters()
    filtersData.value = data
  } catch (e) {
    console.error(e)
  }
}

getFilters()

function optionsFn(date) {
  return filtersData.value.dates
}



watch([city, category, date], async () => {
  await getAllEvents()
})
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;

  &__controls {
    display: flex;
    gap: 20px;
    align-content: center;
  }

  &__select {
    flex-basis: 300px;
  }

  &__cards {
    display: grid;
    grid-template-columns: repeat(4, minmax(300px, 1fr));
    justify-content: center;
    gap: 20px;
  }

  &__card {
    //flex: 0 1 25%;
  }

  &__btn {
    align-self: center;
  }
}
</style>
