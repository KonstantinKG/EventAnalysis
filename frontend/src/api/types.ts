export interface GetAllEventsParams {
  page: number
  date?: string
  city_id?: string
  category_id?: string
}

export interface GetPrisesParams {
  event_id: number
  date: string
}

interface LocationData {
  id: string
  name: string
}

interface CategoryData {
  id: string
  name: string
}

interface CityData {
  id: string
  name: string
}

export interface EventData {
  id: number
  title: string
  photo: string
  description: string
  start: string
  end: string
  url: string
  location: LocationData
  category: CategoryData
  city: CityData
}

export interface AllEventsData {
  current: number
  pages: number
  events: Omit<EventData, 'location'>[]
}

export interface FiltersData {
  cities: CityData[]
  categories: CategoryData[]
  dates: string[]
}

export interface PrisesDatesData {}

interface additionalPropData {
  id: number
  date: string
  prise: number
  seat: string
  available: boolean
}

export interface PrisesData {
  additionalProp1: additionalPropData[]
  additionalProp2: additionalPropData[]
  additionalProp3: additionalPropData[]
}
