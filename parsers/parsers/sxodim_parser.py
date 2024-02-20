import datetime
from logging import Logger

import aiohttp
from bs4 import BeautifulSoup

from helpers import Database


class SxodimParser:
    def __init__(self, logger: Logger, db: Database, session: aiohttp.ClientSession):
        self._logger = logger
        self._db = db
        self._session = session

    async def parse(self):
        parse_from_date = await self._db.get_last_parsed()
        parse_from_date = datetime.date.today() if not parse_from_date else parse_from_date

        main_page_url = 'https://sxodim'
        async with self._session.get(url=main_page_url) as response:
            content = await response.read()
            main_page = BeautifulSoup(content, 'lxml')

        cities = self.get_cities(main_page=main_page)
        for city in cities:
            pass

    @staticmethod
    def get_cities(main_page: BeautifulSoup):
        choices = main_page.find_all(_class="city-choice-title")
        return [choice.text for choice in choices]