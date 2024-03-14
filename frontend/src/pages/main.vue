<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AllEventsData, FiltersData } from 'src/api/types'
import EventAnalysisService from 'src/api'
import EventsControls from 'components/EventsControls.vue'

const eventsData = ref<AllEventsData>({
  current: 1,
  pages: 1,
  events: []
})
const filtersData = ref<FiltersData>({
  categories: [],
  cities: [],
  dates: []
})
const page = ref(1)
const date = ref<string>()
const city = ref<string>()
const category = ref<string>()
const isLoading = ref(false)
const isLoadingMore = ref(false)

function onSelectCategory(id: string) {
  if (category.value && category.value === id) {
    category.value = undefined
  } else {
    category.value = id
  }
}

async function getFilters() {
  try {
    const { data } = await EventAnalysisService.getFilters()
    filtersData.value = data
  } catch (e) {
    console.error(e)
  }
}

async function getAllEvents(loadMore = false) {
  try {
    if (!loadMore) isLoading.value = true
    const { data } = await EventAnalysisService.getAll({
      page: page.value,
      category_id: category.value,
      city_id: city.value,
      date: date.value
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

async function loadMore() {
  isLoadingMore.value = true
  page.value++
  await getAllEvents(true)
  isLoadingMore.value = false
}

watch([city, category, date], async () => {
  page.value = 1
  await getAllEvents()
})

getAllEvents()
getFilters()
</script>

<template>
  <div class="container">
    <div class="page">
      <div class="page__controls">
        <events-controls
          v-model:date="date"
          v-model:city="city"
          v-model:category="category"
          :data="filtersData"
        />
      </div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div v-show="!isLoading" class="page__cards">
          <q-card v-for="event in eventsData.events" :key="event.id" class="page__card">
            <q-img
              class="page__img"
              :src="`files/${event.photo.split(/[\\/]/).pop()}`"
              :alt="`Картинка - ${event.title}`"
              fit="cover"
            >
              <div class="absolute-bottom">
                <span class="cursor-pointer" @click="onSelectCategory(event.category.id)">
                  {{ event.category.name }}
                </span>
              </div>
            </q-img>
            <q-card-section horizontal>
              <q-btn flat :to="{ name: 'Event', params: { id: event.id } }">
                {{ event.title }}
              </q-btn>
            </q-card-section>
            <!--            <q-card-section>-->
            <!--              {{ event.description }}-->
            <!--            </q-card-section>-->
            <q-card-section>
              {{ event.city.name }} {{ event.category.name }} {{ event.start }}
              {{ event.end }}
            </q-card-section>
          </q-card>
          <h5 v-if="!eventsData.events.length && !isLoading">Не найдено мероприятий</h5>
        </div>
      </transition>
      <q-inner-loading :showing="isLoading">
        <q-spinner-hourglass size="xl" color="primary" />
      </q-inner-loading>
      <q-btn
        v-if="eventsData.current < eventsData.pages && !isLoading"
        :loading="isLoadingMore"
        outline
        padding="sm xl"
        class="page__btn"
        color="deep-orange"
        @click="loadMore"
      >
        Показать еще
      </q-btn>
    </div>
  </div>
</template>

<style lang="scss">
.container {
  max-width: $breakpoint-md;
  margin: 0 auto;
  padding: 20px;
}

.page {
  display: flex;
  flex-direction: column;
  gap: 20px;

  &__controls {
    display: flex;
    gap: 20px;
    align-items: center;
    justify-content: center;
  }

  &__select {
    flex-basis: 350px;
  }

  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
  }

  &__card {
    flex-shrink: 1;
    max-width: 250px;
  }

  &__img {
    min-height: 150px;
  }

  &__btn {
    align-self: center;
  }
}
</style>
