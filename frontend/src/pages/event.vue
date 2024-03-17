<script setup lang="ts">
import EventAnalysisService from 'src/api'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref, shallowRef } from 'vue'
import type { EventData, PricesData } from 'src/api/types'

const router = useRouter()
const route = useRoute()

const id = computed(() => route.params.id as string)
const isLoading = ref(false)
const event = ref<EventData>({
  id: '',
  title: '',
  photo: '',
  description: '',
  short_description: '',
  phone: '',
  link: '',
  start: '',
  end: '',
  url: '',
  location: {
    id: '',
    name: ''
  },
  category: {
    id: '',
    name: ''
  },
  city: {
    id: '',
    name: ''
  }
})

const tab = ref('all')
const prices = shallowRef<PricesData>({})

async function getEvent() {
  try {
    const { data } = await EventAnalysisService.getById(id.value)
    event.value = data
  } catch (e) {
    console.error(e)
  }
}

async function getPrices() {
  try {
    isLoading.value = true
    const { data: eventPricesData } = await EventAnalysisService.getEventPrices(id.value)
    if (eventPricesData.length) {
      const { data } = await EventAnalysisService.getPrices({
        event_id: id.value,
        date: eventPricesData[0]
      })
      prices.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

getEvent()
</script>

<template>
  <div class="container">
    <q-btn class="q-mb-sm" icon="arrow_back" unelevated no-caps @click="router.back()">Назад</q-btn>
    <div class="event">
      <q-img :src="`C:\\My Projects\\EventAnalysis\\files\\${event.photo.split(/[\\/]/).pop()}`">
        <div class="image-content absolute-bottom">
          <div>{{ event.category.name }}</div>
          <h4>{{ event.title }}</h4>
        </div>
      </q-img>
      <div class="event__content">
        <div class="event__description" v-html="event.description" />
        <q-card class="event__card">
          <q-card-section>
            {{ event.start }}
          </q-card-section>
          <q-card-section> город {{ event.city.name }}. {{ event.location.name }}</q-card-section>
          <q-card-actions>
            <q-btn color="deep-orange" @click="getPrices">Посмотреть билеты</q-btn>
          </q-card-actions>
        </q-card>
      </div>
      <div v-if="isLoading" class="row justify-center">
        <q-spinner size="xl" color="primary" />
      </div>
      <template v-else-if="Object.keys(prices).length">
        <q-tabs v-model="tab" class="text-deep-orange shadow-1">
          <q-tab name="all" label="Все" />
          <q-tab name="free" label="Свободные" />
          <q-tab name="busy" label="Заняты" />
        </q-tabs>
        <!--        <q-tab-panels v-model="tab" animated swipeable keep-alive>-->
        <!--          <q-tab-panel name="all">all</q-tab-panel>-->
        <!--          <q-tab-panel name="free">free</q-tab-panel>-->
        <!--          <q-tab-panel name="busy">busy</q-tab-panel>-->
        <!--        </q-tab-panels>-->
        <div v-for="(date, index) in Object.keys(prices)" :key="index" class="event__tickets">
          <div
            v-for="item in prices[date]"
            :key="item.id"
            class="event__chips"
          >
            <q-chip color="deep-orange">Дата - {{ item.date }}</q-chip>
            <q-chip v-if="item.price" color="deep-orange">Цена - {{ item.price }}</q-chip>
            <q-chip v-if="item.seat" :color="item.available ? 'deep-orange' : 'grey'">
              Место - {{ item.seat }}
            </q-chip>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.container {
  max-width: $breakpoint-md;
  margin: 0 auto;
  padding: 20px;
}

.q-tab {
  flex-grow: 1;
}

.event {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .image-content {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    width: fit-content;

    h4 {
      margin: 0;
    }
  }

  &__content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 40px;
  }

  &__description {
    align-self: center;
    font-size: 18px;
  }

  &__card {
    flex: 0 0 200px;
  }

  &__tickets {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
  }

  &__chips {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 40px;
  }
}
</style>
