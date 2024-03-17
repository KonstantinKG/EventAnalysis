import { api } from 'boot/axios'
import { AxiosResponse } from 'axios'
import type {
  GetAllEventsParams,
  GetPrisesParams,
  AllEventsData,
  EventData,
  FiltersData,
  PricesData
} from './types'

type PromiseResponse<T> = Promise<{ data: T }>

class EventAnalysisService {
  getData = <T>(response: AxiosResponse<T>) => response.data

  async getAll(params: GetAllEventsParams): PromiseResponse<AllEventsData> {
    return await api.get('/all', { params }).then(this.getData)
  }

  async getById(id: string): PromiseResponse<EventData> {
    return await api.get('/get', { params: { id } }).then(this.getData)
  }

  async getFilters(): PromiseResponse<FiltersData> {
    return await api.get('/get/filters').then(this.getData)
  }

  async getEventPrices(event_id: string): PromiseResponse<string[]> {
    return await api.get('/get/prices/dates', { params: { event_id } }).then(this.getData)
  }

  async getPrices(params: GetPrisesParams): PromiseResponse<PricesData> {
    return await api.get('/get/prices', { params }).then(this.getData)
  }
}

export default new EventAnalysisService()
