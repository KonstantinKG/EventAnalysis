import aiosqlite
from dateutil import parser

from models.table_configurations import TableConfiguration


class Database:
    def __init__(self, config: dict, tables: TableConfiguration):
        self._config = config
        self._tables = tables

    async def insert(self, table: str, columns: list, data: list, on_conflict="ON CONFLICT DO NOTHING"):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))

            query = f"INSERT INTO main.{table}  ({column_names}) VALUES ({placeholders}) {on_conflict}"
            await connection.executemany(query, data)
            await connection.commit()

    async def get_as_dict(self, key: str, value: str, table: str):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"SELECT {key}, {value} FROM main.{table}"
            cursor = await connection.execute(query)
            data = await cursor.fetchall()

        result = dict()
        for row in data:
            result[row[0]] = row[1]
        return result

    async def get_events_as_dict(self):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"SELECT src_id, city_id, start, end, {self._tables.EVENTS.PRIMARY_KEY} FROM main.{self._tables.EVENTS.NAME}"
            cursor = await connection.execute(query)
            data = await cursor.fetchall()

        result = dict()
        for row in data:
            result[f"{row[0]}{row[1]}{row[2]}{row[3]}"] = row[4]
        return result

