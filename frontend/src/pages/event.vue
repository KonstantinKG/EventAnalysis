<script setup lang="ts">
import EventAnalysisService from 'src/api'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref, shallowRef } from 'vue'
import type { EventData, PricesData } from 'src/api/types'
import { formatDate } from 'src/helpers/formatDate'
import { FILES_PATH } from 'src/constants'

const router = useRouter()
const route = useRoute()
const id = computed(() => route.params.id as string)

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
  ticker_url: '',
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
const date = ref('')
const sectors = ref<string[]>([])
const currentSector = ref('')
const pricesData = shallowRef<PricesData>({})
const prices = ref<Set<number>>(new Set([]))
const isLoading = ref(false)

async function getEvent() {
  try {
    const { data } = await EventAnalysisService.getById(id.value)
    event.value = data
  } catch (e) {
    console.error(e)
  }
}

async function getDatePrises() {
  try {
    setTimeout(() => {
      window.scrollTo({ top: document.body.scrollHeight + 46, behavior: 'smooth' })
    })
    isLoading.value = true
    const { data: eventPricesData } = await EventAnalysisService.getEventDatesPrices(id.value)
    date.value = eventPricesData[0]
    if (eventPricesData.length) {
      const { data } = await EventAnalysisService.getEventSectors({
        event_id: id.value,
        date: eventPricesData[0]
      })
      sectors.value = data

      if (!sectors.value.length || !sectors.value[0]) {
        await getPrices()
      }
    } else {
      window.open(event.value.ticker_url || event.value.url, '_blank')
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

async function getPrices(sector?: string) {
  try {
    if (sector) currentSector.value = sector
    isLoading.value = true
    const { data } = await EventAnalysisService.getEventPrices({
      event_id: id.value,
      date: date.value,
      sector
    })
    pricesData.value = data
    if (data) {
      prices.value = new Set([])
      for (const key in data) {
        for (const item of data[key]) {
          if (item.price) prices.value.add(item.price)
        }
      }
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
  <q-page>
    <q-btn class="q-mb-sm" icon="arrow_back" color="deep-orange" no-caps @click="router.back()">
      Назад
    </q-btn>
    <div class="event">
      <q-img :src="`${FILES_PATH}${event.photo.split(/[\\/]/).pop()}`">
        <div class="image-content absolute-bottom">
          <div>{{ event.category.name }}</div>
          <h4>{{ event.title }}</h4>
        </div>
      </q-img>
      <div class="event__content">
        <div>
          <div class="event__description" v-html="event.description" />
          <div class="event__source">
            Источник <a :href="event.url" target="_blank">{{ event.url }}</a>
          </div>
        </div>
        <q-card class="event__card">
          <q-card-section>
            <q-icon color="grey-5" name="event" />
            {{ event.start ? formatDate(event.start) : event.start }}
          </q-card-section>
          <q-card-section v-if="event.phone">
            <q-icon color="grey-5" name="phone" />
            {{ event.phone }}
          </q-card-section>
          <q-card-section v-if="event.link">
            <q-icon color="grey-5" name="language" />
            <a style="word-break: break-all" target="_blank" :href="event.link">
              {{ event.link }}
            </a>
          </q-card-section>
          <q-card-section>город {{ event.city.name }}. {{ event.location.name }}</q-card-section>
          <q-card-actions>
            <q-btn style="width: 100%" color="deep-orange" @click="getDatePrises">
              Посмотреть билеты
            </q-btn>
          </q-card-actions>
        </q-card>
      </div>
      <div v-if="sectors.length && sectors[0] || Object.keys(pricesData).length" style="font-size: 24px; font-weight: 700;">Билеты</div>
      <div v-if="sectors.length && sectors[0]" class="event__sectors">
        <div
          v-for="(sector, index) in sectors"
          :key="index"
          :class="['event__sector', { active: sector === currentSector }]"
          @click="getPrices(sector)"
        >
          {{ sector }}
        </div>
      </div>
      <div v-if="isLoading" class="row justify-center">
        <q-spinner size="xl" color="primary" />
      </div>
      <template v-else-if="sectors.length || Object.values(pricesData).length">
        <div v-if="sectors.length && sectors[0]" style="font-weight: 600; font-size: 20px">
          {{ currentSector }}
        </div>
        <div v-if="prices.size">
          <span style="font-size: 16px">
            <template v-if="prices.size > 1">Цены -</template>
            <template v-else>Цена -</template>
          </span>
          <q-chip
            v-for="(price, index) in prices"
            :key="index"
            :label="`${price.toLocaleString('RU-ru')} ₸`"
            color="blue"
            text-color="white"
          />
        </div>
        <div v-if="currentSector">
          <div style="display: flex; gap: 5px; align-items: center">
            Свободные -
            <div class="event__seat bg-primary" />
          </div>
          <div style="display: flex; gap: 5px; align-items: center">
            Заняты -
            <div class="event__seat bg-grey" />
          </div>
        </div>
        <div v-for="key in Object.keys(pricesData)" :key="key" style="display: flex; gap: 20px">
          <template v-if="key !== 'rates'">
            <span style="flex: 0 0 45px">{{ key }} ряд</span>
            <div class="event__seats">
              <div
                v-for="item in pricesData[key]"
                :key="item.id"
                :class="[
                  'event__seat',
                  {
                    'bg-grey': !item.available,
                    'bg-primary': item.available
                  }
                ]"
              />
            </div>
          </template>
          <div v-else style="font-size: 16px">
            Дата -
            <q-chip text-color="white" color="blue">{{ formatDate(pricesData[key][0].date) }}</q-chip>
          </div>
        </div>
        <q-btn
          v-if="Object.keys(pricesData).length"
          style="width: 200px"
          color="deep-orange"
          no-caps
          target="_blank"
          :href="event.ticker_url || event.url"
        >
          Купить билет
        </q-btn>
      </template>
    </div>
  </q-page>
</template>

<style scoped lang="scss">
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
    flex: 0 0 300px;
    font-size: 16px;

    .q-card__section {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .q-card__section--vert {
      padding: 10px 16px;
    }
  }

  &__sectors {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  &__sector {
    background-color: $deep-orange;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    cursor: pointer;
    border-radius: 20px;
    transition: background-color 0.3s;

    &.active {
      background-color: $red-14;
    }

    &:hover {
      background-color: $deep-orange-3;
    }
  }

  &__tickets {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
  }

  &__source {
    font-size: 16px;
    font-weight: 500;
  }

  &__seats {
    flex-grow: 1;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }

  &__seat {
    flex: 0 0 16px;
    height: 16px;
    border-radius: 4px;
  }
}
</style>
