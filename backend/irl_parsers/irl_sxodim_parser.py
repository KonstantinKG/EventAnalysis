import uuid
from datetime import datetime
from logging import Logger

import aiohttp
import ephem
from bs4 import BeautifulSoup
from dateutil import parser

from helpers import Database
from models import EventPrice, Event
from models.table_configurations import TableConfiguration


class IrlSxodimParser:
    DOMAIN = 'https://sxodim.com'

    def __init__(self, config: dict, logger: Logger, db: Database):
        self._config = config
        self._logger = logger
        self._db = db
        self._session = aiohttp.ClientSession(trust_env=True)
        self._tables = TableConfiguration()

    @staticmethod
    def parse_date(date: str) -> int or None:
        try:
            parsed_date = parser.parse(date)
            return ephem.julian_date(parsed_date)
        except Exception:
            return None

    async def parse_available_dates(self, ticket_url: str):
        page = await self.get_event_ticket_page(url=ticket_url)
        entry_ticket = page.find('div', class_='entry-ticket entry-tickets-card disabled')
        hall_item = page.find('div', class_='tickets-hall-item')
        id = entry_ticket.attrs['data-id'] if entry_ticket else hall_item.attrs['data-id']

        ticket_url = f"{self.DOMAIN}/api/tickets/{id}"
        ticket = await self.get_event_ticket(url=ticket_url)

        available_dates = ticket["data"].get("availableDates")
        return available_dates

    async def parse_event_prices(self, event: Event, available_date: str):
        upload = list()

        page = await self.get_event_ticket_page(url=event.ticket_url)
        entry_ticket = page.find('div', class_='entry-ticket entry-tickets-card disabled')
        hall_item = page.find('div', class_='tickets-hall-item')
        id = entry_ticket.attrs['data-id'] if entry_ticket else hall_item.attrs['data-id']

        ticket_url = f"{self.DOMAIN}/api/tickets/{id}"

        date = datetime.strptime(available_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        timeslots = await self.get_ticket_timeslots(url=ticket_url, date=available_date)
        if len(timeslots) > 0:
            for timeslot in timeslots:
                rates = await self.get_event_timeslot_rates(url=ticket_url, date=date, time=timeslot["time_short"])
                hall = await self.get_event_timeslot_hall(url=ticket_url, date=date, time=timeslot["time_short"])

                if hall is None:
                    for rate in rates.values():
                        price = EventPrice(
                            id=str(uuid.uuid4()),
                            event_id=event.id,
                            date=self.parse_date(f"{available_date} {timeslot['time']}"),
                            price=rate["price"],
                            seat='',
                            sector='',
                            available=None
                        )
                        upload.append(price)

                else:
                    for seat in hall["seats"]:
                        price = EventPrice(
                            id=str(uuid.uuid4()),
                            event_id=event.id,
                            date=self.parse_date(f"{available_date} {timeslot['time']}"),
                            price=seat["seatPrice"]["rate"]["price"] if seat["seatPrice"] else None,
                            sector=f"{seat['sector_name']}",
                            seat=f"{seat['row']} ряд {seat['column']} место",
                            available=seat["available"]
                        )
                        upload.append(price)
        else:
            rates = await self.get_event_timeslot_rates(url=ticket_url, date=date)
            for rate in rates.values():
                price = EventPrice(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    date=self.parse_date(available_date),
                    price=rate["price"],
                    seat="",
                    available=None
                )
                upload.append(price)

        await self._db.insert(
            table=self._tables.EVENTS_PRICES.NAME,
            columns=self._tables.EVENTS_PRICES.COLUMNS,
            data=[
                [item.__dict__.get(col) for col in self._tables.EVENTS_PRICES.COLUMNS]
                for item in upload
            ],
            on_conflict=self._tables.EVENTS_PRICES.ON_CONFLICT
        )

    async def get_event_ticket_page(self, url: str) -> BeautifulSoup:
        async with self._session.get(url=url) as response:
            content = await response.read()
        return BeautifulSoup(content, "lxml")

    async def get_event_ticket(self, url: str) -> dict:
        async with self._session.get(url=url) as response:
            return await response.json()

    async def get_ticket_timeslots(self, url: str, date: str) -> list[dict]:
        try:
            async with self._session.post(url=f"{url}/timeslots", json={"date": f"{date}T00:00:00.000Z"}) as response:
                timeslots = await response.json()
            return timeslots["data"]
        except:
            return list()

    async def get_event_timeslot_rates(self, url: str, date: str, time: str = None) -> dict:
        result = dict()

        timeslot_url = f"{url}/date-rates"
        params = {"date": date, "time": time}
        if not time:
            params.__delitem__("time")

        async with self._session.get(url=timeslot_url, params=params) as response:
            rates = await response.json()

        for rate in rates["data"]:
            result[rate["rate_id"]] = rate

        return result

    async def get_event_timeslot_hall(self, url: str, date: str, time: str) -> dict or None:
        params = {"date": date, "time": time}
        async with self._session.get(url=f"{url}/hall", params=params) as response:
            if "html" in response.content_type:
                return None
            hall = await response.json()
        return hall["data"]
