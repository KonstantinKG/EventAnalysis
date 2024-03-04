import traceback
from datetime import datetime, timedelta
from logging import Logger
from aiohttp.web_request import Request

from helpers import Database
from irl_parsers import IrlSxodimParser
from models import Event


class EventAnalysisController:
    def __init__(self, config: dict, logger: Logger, db: Database):
        self._config = config
        self._logger = logger
        self._db = db

    @staticmethod
    def to_date(date: str) -> datetime or None:
        try:
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    @staticmethod
    def response(data) -> dict:
        return {"data": data}

    @staticmethod
    def error(errors) -> dict:
        return {"errors": errors}

    async def get(self, request: Request) -> dict:
        try:
            id = request.query.get("id")
            event = await self._db.get_event(id=id)
            if not event:
                return self.response(data={})

            return self.response(data={
                "id": event[0],
                "title": event[1],
                "photo": event[2],
                "description": event[3],
                "short_description": event[15],
                "phone": event[4],
                "link": event[5],
                "start": event[6],
                "end": event[7],
                "url": event[8],
                "location": {
                    "id": event[9],
                    "name": event[10]
                },
                "category": {
                    "id": event[11],
                    "name": event[12]
                },
                "city": {
                    "id": event[13],
                    "name": event[14]
                }
            })
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")
            return self.error(errors=[e])

    async def all(self, request: Request) -> dict:
        try:
            page = int(request.query.get("page"))
            date = request.query.get("date")
            city_id = request.query.get("city_id")
            category_id = request.query.get("category_id")

            limit = 20
            offset = (page - 1) * limit
            total = await self._db.count_all_events(date=date, city_id=city_id, category_id=category_id)
            pages = int(total / limit + (total % 1 if limit > 0 else 0))

            events = await self._db.all_events(offset=offset, limit=limit, date=date, city_id=city_id,
                                               category_id=category_id)

            return self.response(data={
                "current": page,
                "pages": pages,
                "events": [{
                    "id": event[0],
                    "title": event[1],
                    "photo": event[2],
                    "description": event[3],
                    "start": event[4],
                    "end": event[5],
                    "url": event[6],
                    "category": {
                        "id": event[7],
                        "name": event[8]
                    },
                    "city": {
                        "id": event[9],
                        "name": event[10]
                    }
                } for event in events]
            })

        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")
            return self.error(errors=[e])

    async def get_available_dates(self, request: Request):
        try:
            event_id = request.query.get("event_id")

            event_row = await self._db.get_event(id=event_id)
            event = Event(id=event_row[0], ticket_url=event_row[-1])

            parser = IrlSxodimParser(config=self._config, logger=self._logger, db=self._db)
            dates = await parser.parse_available_dates(ticket_url=event.ticket_url)
            return self.response(data=dates)
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")
            return self.response(data=[])

    async def get_prices(self, request: Request) -> dict:
        try:
            event_id = request.query.get("event_id")
            available_date = request.query.get("date")

            event_row = await self._db.get_event(id=event_id)
            event = Event(id=event_row[0], ticket_url=event_row[-1])

            parser = IrlSxodimParser(config=self._config, logger=self._logger, db=self._db)
            await parser.parse_event_prices(event=event, available_date=available_date)

            prices = await self._db.get_event_prices(id=event_id, date=available_date)
            data = {}

            for price in prices:
                if price[1] not in data:
                    data[price[1]] = list()

                data[price[1]].append({
                    "id": price[0],
                    "date": price[1],
                    "price": price[2],
                    "seat": price[3],
                    "available": price[4]
                })

            return self.response(data=data)

        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")
            return self.error(errors=[e])

    async def get_filters(self, request: Request) -> dict:
        try:
            cities = await self._db.get_cities()
            categories = await self._db.get_categories()
            dates = await self._db.get_dates()

            return self.response(data={
                "cities": cities,
                "categories": categories,
                "dates": dates
            })
        except Exception as e:
            self._logger.error(f"{e} {traceback.format_exc()}")
            return self.error(errors=[e])
