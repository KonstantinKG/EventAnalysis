import asyncio
import datetime
import json
import os
import traceback
import uuid

import aiofiles
import ephem
from logging import Logger

import aiohttp
from dateutil import parser
from bs4 import BeautifulSoup

from helpers import Database, ForeignKeyMapper, Storage
from models import City, Event, Category, Location
from models.table_configurations import TableConfiguration


class SxodimParser:
    DOMAIN = 'https://sxodim.com'

    def __init__(self, config: dict, logger: Logger, db: Database, tables: TableConfiguration,
                 session: aiohttp.ClientSession):
        self._db = db
        self._config = config
        self._logger = logger
        self._session = session
        self._storage = Storage()
        self._tables = tables
        self._mapper = ForeignKeyMapper(db=db, tables=tables)

    @staticmethod
    def parse_date(date: str) -> int or None:
        try:
            parsed_date = parser.parse(date)
            return ephem.julian_date(parsed_date)
        except Exception:
            return None

    @staticmethod
    def rm(value: str) -> str or None:
        try:
            return value.replace("&nbsp;", "").replace(" ", "").replace("\n", "").replace("\t", "")
        except AttributeError:
            return None

    async def parse(self):
        await self._mapper.fill_all()

        async with self._session.get(url=self.DOMAIN) as response:
            content = await response.read()
            main_page = BeautifulSoup(content, 'lxml')

        cities = self.parse_cities(main_page=main_page)
        self._storage.Cities = cities.copy()

        for city in cities:
            await self.parse_city_events(slug=city.slug)

    async def upload(self):
        await self._db.insert(
            table=self._tables.CATEGORIES.NAME,
            columns=self._tables.CATEGORIES.COLUMNS,
            data=[
                [item.__dict__.get(col) for col in self._tables.CATEGORIES.COLUMNS]
                for item in self._storage.Categories
            ],
            on_conflict=self._tables.CATEGORIES.ON_CONFLICT
        )
        await self._db.insert(
            table=self._tables.CITIES.NAME,
            columns=self._tables.CITIES.COLUMNS,
            data=[
                [item.__dict__.get(col) for col in self._tables.CITIES.COLUMNS]
                for item in self._storage.Cities
            ],
            on_conflict=self._tables.CITIES.ON_CONFLICT
        )
        await self._db.insert(
            table=self._tables.EVENTS.NAME,
            columns=self._tables.EVENTS.COLUMNS,
            data=[
                [item.__dict__.get(col) for col in self._tables.EVENTS.COLUMNS]
                for item in self._storage.Events
            ],
            on_conflict=self._tables.EVENTS.ON_CONFLICT
        )
        await self._db.insert(
            table=self._tables.LOCATIONS.NAME,
            columns=self._tables.LOCATIONS.COLUMNS,
            data=[
                [item.__dict__.get(col) for col in self._tables.LOCATIONS.COLUMNS]
                for item in self._storage.Locations
            ],
            on_conflict=self._tables.LOCATIONS.ON_CONFLICT
        )

        self._storage.clear()

    def parse_cities(self, main_page: BeautifulSoup) -> list[City]:
        result = list()

        container = main_page.find(id='city-select-container')
        cities = json.loads(container.attrs["data-cities"])

        for city in cities:
            city_id = self._mapper.Cities.get(city["name"])
            if city_id is None:
                city_id = str(uuid.uuid4())
                self._mapper.Cities[city["name"]] = city_id

            city = City(id=city_id, name=city["name"], slug=city["slug"])
            result.append(city)

        return result

    async def parse_city_events(self, slug: str):
        city_page = await self.get_city_page(slug=slug)
        allowed_dates = self.get_city_dates(city_page=city_page)

        page = 1
        for date in allowed_dates:
            while True:
                attempts = 3
                try:
                    self._logger.info(f"Parsing events. city: {slug} date: {date} page: {page}")
                    city_events = await self.get_city_events(city=slug, date=date, page=page)
                    if len(city_events) == 0:
                        break

                    for city_event in city_events:
                        await self.parse_city_event(event=city_event)

                    page += 1
                except Exception as e:
                    attempts -= 1
                    if attempts == 0:
                        self._logger.error(e, traceback.format_exc())
                        break

                    await asyncio.sleep(1)
                    self._logger.error(e)

            await asyncio.sleep(2)
            await self.upload()
            page = 1

    async def get_city_page(self, slug: str) -> BeautifulSoup:
        city_url = f"{self.DOMAIN}/{slug}"
        async with self._session.get(url=city_url) as response:
            content = await response.read()
            return BeautifulSoup(content, 'lxml')

    @staticmethod
    def get_city_dates(city_page: BeautifulSoup) -> list:
        calendar_days = city_page.find_all(class_='calendar-day')
        return [day.attrs["data-value"] for day in calendar_days]

    async def get_city_events(self, city: str, date: str, page: int) -> list:
        city_events_url = f"{self.DOMAIN}/api/posts/in/{city}?date={date}&page={page}"
        async with self._session.get(url=city_events_url) as response:
            content = await response.read()
            parsed = json.loads(content)
        return parsed["data"]

    def parse_city_event_category(self, event: dict):
        category_name = event["category"]["name"]
        category_id = self._mapper.Categories.get(category_name)

        if category_id is None:
            category_id = str(uuid.uuid4())
            self._mapper.Categories[category_name] = category_id

        return Category(
            id=category_id,
            name=category_name,
        )

    async def parse_city_event(self, event: dict):
        url = f"{self.DOMAIN}/{event['city']['slug']}/event/{event['slug']}"
        page = await self.get_city_event_page(url=url)

        category = self.parse_city_event_category(event=event)

        location = self.get_event_page_location(page=page)
        location_id = None
        if location is not None:
            location_id = location.id
            self._storage.Locations.add(location)

        source = self._mapper.Sources.value.get("sxodim")

        dates = event["event_dates"]
        start_date = self.parse_date(dates[0]["date_from"])
        end_date = self.parse_date(dates[-1]["date_to"]) if dates[-1].get("date_to") else self.parse_date(dates[-1]["date_from"])

        photo = await self.save_photo(event["image"])

        event = Event(
            id=None,
            src_id=event['id'],
            title=event["name"],
            photo=photo,
            description=self.get_event_page_description(page=page),
            short_description=self.rm(event["description"]),
            phone=self.get_event_page_phone(page=page),
            link=self.get_event_page_link(page=page),
            start=start_date,
            end=end_date,
            location_id=location_id,
            category_id=category.id,
            city_id=self._mapper.Cities.get(event["city"]["name"]),
            url=url,
            ticket_url=self.get_event_page_buy_url(page=page),
            source_id=source.id if source is not None else None
        )

        id = self._mapper.Events.get(f"{event.src_id}{event.city_id}{event.start}{event.end}")
        if id is None:
            id = str(uuid.uuid4())

        event.id = id

        self._storage.Categories.add(category)
        self._storage.Events.add(event)

    async def get_city_event_page(self, url: str) -> BeautifulSoup:
        async with self._session.get(url=url) as response:
            content = await response.read()
        return BeautifulSoup(content, "lxml")

    def get_event_page_description(self, page: BeautifulSoup):
        result = ""

        paragraphs = page.select(".content_wrapper > p")
        for paragraph in paragraphs:
            images = paragraph.select("img")
            if len(images) > 0:
                continue

            content = self.rm(paragraph.prettify())
            result += content

        return result

    def get_event_page_location(self, page: BeautifulSoup) -> Location or None:
        try:
            location_svg = page.find(class_="svg-icon--location")
            location_div = location_svg.find_next(class_="text")
            if location_div is None:
                return None

            location = Location(id=str(uuid.uuid4()), name=self.rm(location_div.text))
            if self._mapper.Locations.get(location.name) is None:
                self._mapper.Locations[location.name] = location.id

            return location
        except:
            return None

    def get_event_page_phone(self, page: BeautifulSoup) -> str or None:
        phone_div = page.select(".group > div.number")
        if len(phone_div) == 0:
            return None

        phone = self.rm(phone_div[0].text)
        return phone

    @staticmethod
    def get_event_page_buy_url(page: BeautifulSoup) -> str or None:
        buy_ticket_link = page.select(".buy-ticket > a")
        if len(buy_ticket_link) == 0:
            return None
        return buy_ticket_link[0]["href"]

    @staticmethod
    def get_event_page_link(page: BeautifulSoup) -> str or None:
        link_tag = page.select(".more_info > .group > .text > a")
        if len(link_tag) == 0:
            return None

        link = link_tag[0]["href"]
        return link

    async def save_photo(self, url: str) -> str | None:
        attempts = 3
        try:
            while True:
                async with self._session.get(url=url) as response:
                    if response.status != 200:
                        raise Exception(f"Incorrect response status {response.status}")

                    file_bytes = await response.read()
                    filename = url.split("/")[-1]
                    save_directory = self._config["files"]
                    os.makedirs(save_directory, exist_ok=True)
                    file_path = os.path.join(save_directory, filename)

                    if os.path.exists(file_path):
                        return file_path

                    async with aiofiles.open(file_path, 'wb') as file:
                        await file.write(file_bytes)

                    return file_path

        except Exception as e:
            attempts -= 1
            if attempts == 0:
                self._logger.error(e, traceback.format_exc())
                return None
            self._logger.error(e)
