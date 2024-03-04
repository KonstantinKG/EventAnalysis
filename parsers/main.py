import json
import asyncio
import logging.config
import traceback
import aiohttp
import time

from helpers import Database
from models.Sources import Sources
from models.table_configurations import TableConfiguration
from parsers import SxodimParser

config: dict
logger: logging.Logger
session: aiohttp.ClientSession


def timer(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        value = await func(*args, **kwargs)
        print(f"Function {func.__name__} end up in: {time.time() - start} seconds")
        return value

    return wrapper


@timer
async def main():
    global config, logger, session

    with open("config.json", 'r', encoding='utf-8') as file:
        config = json.load(file)

    logging.config.dictConfig(config=config["logger"])
    logger = logging.getLogger(name=config["app"])


    session = aiohttp.ClientSession(trust_env=True)

    tables = TableConfiguration()

    db = Database(config=config, tables=tables)

    await db.insert(
        table=tables.SOURCES.NAME,
        columns=tables.SOURCES.COLUMNS,
        data=[
            [source.__dict__.get(col) for col in tables.SOURCES.COLUMNS]
            for source in Sources().value.values()
        ]
    )

    sxodim_parser = SxodimParser(
        config=config,
        logger=logger,
        db=db,
        session=session,
        tables=tables
    )

    try:
        logger.info(f"Parser started")
        await sxodim_parser.parse()
    except Exception as err:
        logger.fatal(f"Parser failed with error {err}\nTRACEBACK: {traceback.format_exc()}")
    finally:
        await close_connections()


async def close_connections():
    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
