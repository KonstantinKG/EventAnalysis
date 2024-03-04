import asyncio

from helpers import Database
from models.Sources import Sources
from models.table_configurations import TableConfiguration


class ForeignKeyMapper:
    def __init__(self, db: Database, tables: TableConfiguration):
        self._db = db
        self._tables = tables
        self.Cities = dict()
        self.Categories = dict()
        self.Locations = dict()
        self.Events = dict()
        self.Dates = dict()
        self.Sources = Sources()

    async def fill_all(self):
        await asyncio.gather(
            self.fill_cities(),
            self.fill_categories(),
            self.fill_locations(),
            self.fill_events()
        )

    async def fill_cities(self):
        self.Cities = await self._db.get_as_dict(
            self._tables.CITIES.UNIQUE_COLUMN,
            self._tables.CITIES.PRIMARY_KEY,
            self._tables.CITIES.NAME,
        )

    async def fill_categories(self):
        self.Categories = await self._db.get_as_dict(
            self._tables.CATEGORIES.UNIQUE_COLUMN,
            self._tables.CATEGORIES.PRIMARY_KEY,
            self._tables.CATEGORIES.NAME,
        )

    async def fill_locations(self):
        self.Categories = await self._db.get_as_dict(
            self._tables.LOCATIONS.UNIQUE_COLUMN,
            self._tables.LOCATIONS.PRIMARY_KEY,
            self._tables.LOCATIONS.NAME,
        )

    async def fill_events(self):
        self.Events = await self._db.get_events_as_dict()
