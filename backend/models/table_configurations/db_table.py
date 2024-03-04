class DbTable:
    def __init__(self, table: str, columns: list, on_conflict: str, primary_key: str = None, unique_column: str = None):
        self.NAME = table
        self.COLUMNS = columns
        self.ON_CONFLICT = on_conflict
        self.PRIMARY_KEY = primary_key
        self.UNIQUE_COLUMN = unique_column
