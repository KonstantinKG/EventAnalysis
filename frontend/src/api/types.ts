export interface GetAllEventsParams {
  page: number
  date?: string
  city_id?: string
  category_id?: string
}

export interface GetPrisesParams {
  event_id: string
  date: string
  sector?: string
}

export interface SearchParams {
  title: string
  page: number
}

export interface SectorsParams {
  event_id: string
  date: string
}

type Item = { id: string; name: string }

type LocationData = Item
type CategoryData = Item
type CityData = Item

export interface EventData {
  id: string
  title: string
  photo: string
  description: string
  short_description: string
  phone: string
  link: string
  start: string
  end: string
  url: string
  ticker_url: string
  location: LocationData
  category: CategoryData
  city: CityData
}

export interface AllEventsData {
  total: number
  current: number
  pages: number
  events: Omit<EventData, 'location' | 'short_description' | 'phone' | 'link' | 'ticker_url'>[]
}

export interface FiltersData {
  cities: CityData[]
  categories: CategoryData[]
  dates: string[]
}

interface EntryTicket {
  id: number
  date: string
  price: number
  seat: string
  available: boolean
}

export type PricesData = Record<string, EntryTicket[] | never>
