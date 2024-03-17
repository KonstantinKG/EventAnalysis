import aiosqlite


class Database:
    def __init__(self, config: dict):
        self._config = config

    async def insert(self, table: str, columns: list, data: list, on_conflict="ON CONFLICT DO NOTHING"):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))

            query = f"INSERT INTO main.{table}  ({column_names}) VALUES ({placeholders}) {on_conflict}"
            await connection.executemany(query, data)
            await connection.commit()

    async def get_event(self, id) -> list:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"""
                SELECT
                    e.id,
                    title,
                    photo,
                    description,
                    phone,
                    link,
                    datetime(start),
                    datetime(end),
                    url,
                    l.id,
                    l.name,
                    ct.id,
                    ct.name,
                    ci.id,
                    ci.name,
                    short_description,
                    ticket_url
                FROM events e
                INNER JOIN locations l ON location_id = l.id
                INNER JOIN categories ct ON category_id = ct.id
                INNER JOIN cities ci ON city_id = ci.id
                WHERE e.id = '{id}'
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows[0] if len(rows) > 0 else None

    async def get_event_ticket_url(self, id) -> str:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"""
                SELECT
                    ticket_url
                FROM events e
                WHERE e.id = '{id}'
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows[0][0]

    async def all_events(self, offset, limit, date, city_id, category_id) -> list:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            condition = self.get_all_events_filter(date, city_id, category_id)

            query = f"""
                SELECT
                    e.id,
                    title,
                    photo,
                    short_description,
                    datetime(start),
                    datetime(end),
                    url,
                    ct.id,
                    ct.name,
                    ci.id,
                    ci.name
                FROM events e
                INNER JOIN locations l ON location_id = l.id
                INNER JOIN categories ct ON category_id = ct.id
                INNER JOIN cities ci ON city_id = ci.id
               {condition}
                LIMIT {limit}
                OFFSET {offset}
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows

    async def get_event_sectors(self, id, date) -> list:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"""
                SELECT DISTINCT sector FROM events_prices e
                WHERE e.event_id = '{id}' AND date(e.date) = date('{date}')
                ORDER BY price 
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows

    async def get_event_prices(self, id, date, sector: str = None) -> list:
        condition = f"WHERE e.event_id = '{id}' AND date(e.date) = date('{date}')"
        condition = condition if not sector else f"{condition} AND sector = '{sector}'"
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"""
                SELECT
                    e.id,
                    datetime(date),
                    price,
                    seat,
                    available,
                    sector
                FROM events_prices e
                {condition}
                ORDER BY available DESC, price
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows

    async def count_all_events(self, date, city_id, category_id) -> int:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            condition = self.get_all_events_filter(date, city_id, category_id)
            query = f"""
                SELECT
                    count(*)
                FROM events e
                {condition}
            """

            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return int(rows[0][0])

    @staticmethod
    def get_all_events_filter(date, city_id, category_id):
        date_query = f"date(start) >= date() AND (date(start) >= date('{date}') AND date(end) <= date('{date}'))" if date else ""
        city_query = f"city_id = '{city_id}'" if city_id else ""
        category_query = f"category_id = '{category_id}'" if category_id else ""

        condition = "WHERE date(start) >= date()"
        if date_query:
            condition += f" AND {date_query}"

        if city_query:
            condition += f"AND {city_query}"

        if category_query:
            condition += f"AND {category_query}"

        return condition

    async def get_cities(self):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = "SELECT id, name FROM cities"
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

    async def get_categories(self):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = "SELECT id, name FROM categories"
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

    async def get_dates(self):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = """
                WITH dates AS (
                    SELECT start as date FROM events WHERE start IS NOT null
                    UNION ALL
                    SELECT end as date FROM events WHERE end IS NOT null
                )
                SELECT DISTINCT date(date) FROM dates WHERE date(date) >= date() ORDER BY date
            """
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def search_event(self, query: str, offset: int, limit: int) -> list:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f'''
                SELECT
                    e.id,
                    title,
                    photo,
                    short_description,
                    datetime(start),
                    datetime(end),
                    url,
                    ct.id,
                    ct.name,
                    ci.id,
                    ci.name
                FROM events e
                INNER JOIN locations l ON location_id = l.id
                INNER JOIN categories ct ON category_id = ct.id
                INNER JOIN cities ci ON city_id = ci.id
                WHERE e.title LIKE '%{query}%'
                LIMIT {limit}
                OFFSET {offset}
            '''
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return rows

    async def get_search_event_count(self, query: str) -> int:
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f'''SELECT count(*) FROM events e WHERE e.title LIKE '%{query}%';'''
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
        return int(rows[0][0])

    async def get_as_dict(self, key: str, value: str, table: str):
        async with aiosqlite.connect(self._config['connection']['sqlite']) as connection:
            query = f"SELECT {key}, {value} FROM main.{table}"
            cursor = await connection.execute(query)
            data = await cursor.fetchall()

        result = dict()
        for row in data:
            result[row[0]] = row[1]
        return result