<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AllEventsData, FiltersData } from 'src/api/types'
import EventAnalysisService from 'src/api'
import EventsControls from 'components/EventsControls.vue'
import { formatDate } from 'src/helpers/formatDate'
import { useQuasar } from 'quasar'
import { FILES_PATH } from 'src/constants'

const eventsData = ref<AllEventsData>({
  total: 0,
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

const $q = useQuasar()
const isDarkMode = ref($q.dark.isActive)

function toggleTheme(value: boolean) {
  isDarkMode.value = value
  $q.dark.set(value)
}

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
    filtersData.value.categories = data.categories
    filtersData.value.cities = data.cities
    filtersData.value.dates = data.dates.map((el) => {
      return el.split('-').join('/')
    })
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

async function onSearch(value: string) {
  try {
    isLoading.value = true
    const { data } = await EventAnalysisService.search({
      title: value,
      page: page.value
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

watch([city, category, date], async () => {
  page.value = 1
  await getAllEvents()
})

getAllEvents()
getFilters()
</script>

<template>
  <q-page>
    <div class="events">
      <events-controls
        v-model:city="city"
        v-model:category="category"
        :data="filtersData"
        @search="onSearch"
        @clear="getAllEvents"
      />
      <div class="row items-center justify-between">
        <div class="title">Всего найдено мероприятий: {{ eventsData.total }}</div>
        <div>
          <q-toggle
            class="dark-mode"
            size="lg"
            color="blue"
            checked-icon="dark_mode"
            unchecked-icon="light_mode"
            :model-value="isDarkMode"
            @update:model-value="toggleTheme"
          />
          <q-btn
            class="events__date"
            icon="event"
            round
            :color="$q.dark.isActive ? 'grey-9' : 'grey-13'"
          >
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-date
                v-model="date"
                today-btn
                mask="YYYY-MM-DD"
                color="deep-orange"
                :options="filtersData.dates"
              />
            </q-popup-proxy>
          </q-btn>
        </div>
      </div>
      <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
        <div v-if="!isLoading" class="events__cards">
          <q-card v-for="event in eventsData.events" :key="event.id" class="events__card">
            <q-img
              class="events__img"
              :src="`${FILES_PATH}${event.photo.split(/[\\/]/).pop()}`"
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
              <q-btn
                style="width: 100%"
                no-caps
                color="grey-9"
                :to="{ name: 'Event', params: { id: event.id } }"
              >
                {{ event.title }}
              </q-btn>
            </q-card-section>
            <q-card-section>
              город {{ event.city.name }}, {{ formatDate(event.start) }}
            </q-card-section>
          </q-card>
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
        class="events__btn"
        color="deep-orange"
        @click="loadMore"
      >
        Показать еще
      </q-btn>
    </div>
  </q-page>
</template>

<style scoped lang="scss">
.container {
  max-width: $breakpoint-md;
  margin: 0 auto;
  padding: 20px;
}

.title {
  font-weight: 600;
  font-size: 24px;
}

.events {
  display: flex;
  flex-direction: column;
  gap: 20px;

  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
  }

  &__card {
    max-width: 250px;
    width: 100%;
  }

  &__img {
    min-height: 150px;
  }

  &__btn {
    align-self: center;
  }
}
</style>
