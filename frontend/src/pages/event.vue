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
    <q-btn icon="arrow_back" @click="router.back()">Назад</q-btn>
    <div class="event">
      <q-img :src="`files/${event.photo.split(/[\\/]/).pop()}`">
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
        <q-tabs v-model="tab" class="text-deep-orange">
          <q-tab name="all" label="Все" />
          <q-tab name="free" label="Свободные" />
          <q-tab name="busy" label="Заняты" />
        </q-tabs>
        <div v-for="(date, index) in Object.keys(prices)" :key="index" class="row">
          <q-chip>{{ date }}</q-chip>
          <div
            v-for="item in prices[date]"
            :key="item.id"
            class="chips"
            style="margin-bottom: 40px"
          >
            <q-chip color="deep-orange">Дата - {{ item.date }}</q-chip>
            <q-chip color="deep-orange">Цена - {{ item.price }}</q-chip>
            <q-chip :color="item.available ? 'deep-orange' : 'grey'">
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

.event {
  display: flex;
  flex-direction: column;
  gap: 20px;

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
}

.image-content {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  width: fit-content;

  h4 {
    margin: 0;
  }
}

.chips {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
