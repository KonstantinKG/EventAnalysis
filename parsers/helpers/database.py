import aiosqlite
from dateutil import parser


class Database:
    def __init__(self, config: dict):
        self._config = config

    async def get_last_parsed(self):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"SELECT last_parsed FROM parsers WHERE name = {self._config['app']}"
            cursor = await connection.execute(query)
            data = await cursor.fetchall()

        return parser.parse(data[0]) if len(data) > 0 else None

    async def insert(self, table: str, columns: list, data: list):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))

            query = f"INSERT INTO {table}  ({column_names}) VALUES ({placeholders})"
            await connection.executemany(query, data)
            await connection.commit()