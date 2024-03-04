from models.table_configurations.db_table import DbTable


class TableConfiguration:
    def __init__(self):
        self.SOURCES = DbTable(
            table="sources",
            columns=["id", "name", "slug"],
            on_conflict="on conflict do nothing",
            primary_key="id",
            unique_column="slug"
        )

        self.CITIES = DbTable(
            table="cities",
            columns=["id", "name"],
            on_conflict="on conflict do nothing",
            primary_key="id",
            unique_column="name"
        )

        self.CATEGORIES = DbTable(
            table="categories",
            columns=["id", "name"],
            on_conflict="on conflict do nothing",
            primary_key="id",
            unique_column="name"
        )

        self.LOCATIONS = DbTable(
            table="locations",
            columns=["id", "name"],
            on_conflict=f"on conflict do nothing",
            primary_key="id",
            unique_column="name"
        )

        event_columns = [
            "id", "src_id", "title", "photo", "short_description", "description", "phone",
            "link", "start", "end", "location_id", "source_id", "city_id", "url", "category_id"
        ]
        self.EVENTS = DbTable(
            table="events",
            columns=event_columns,
            on_conflict=f"on conflict (title, start_date) do update set {', '.join(f'{c} = EXCLUDED.{c}' for c in event_columns)}",
            primary_key="id"
        )

        self.EVENTS_PRICES = DbTable(
            table="events_prices",
            columns=["id", "event_id", "date", "price", "seat", "available"],
            on_conflict=f"on conflict (event_id, date, price, seat) do update set available = EXCLUDED.available"
        )
