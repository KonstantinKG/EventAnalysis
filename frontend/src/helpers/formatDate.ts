import { MONTHS } from 'src/constants'

export function formatDate(date: string) {
  if (!date) {
    throw new Error('invalid date')
  }

  const [datePart, timePart] = date.split(' ')
  const [year, month, day] = datePart.split('-')
  const [hours, minutes] = timePart.split(':')

  return `${parseInt(day)} ${MONTHS[parseInt(month) - 1]} в ${hours}:${minutes}`
}
