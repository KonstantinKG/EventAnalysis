export function formatDate(date: string) {
  if (!date) {
    throw new Error('invalid date')
  }

  const months = [
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря'
  ]

  const [datePart, timePart] = date.split(' ')
  const [year, month, day] = datePart.split('-')
  const [hours, minutes] = timePart.split(':')

  return `${parseInt(day)} ${months[parseInt(month) - 1]} в ${hours}:${minutes}`
}
