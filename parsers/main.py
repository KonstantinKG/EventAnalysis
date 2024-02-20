import sys
import json
import asyncio

import logging.config
import time
import traceback
from logging import Logger

import aiohttp

from helpers import Database
from parsers import SxodimParser

config: dict
logger: Logger
session: aiohttp.ClientSession

def timer(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        value = await func(*args, **kwargs)
        print(f"Parser end up in: {time.time() - start}")
        return value

    return wrapper


@timer
async def main():
    global config, logger

    with open("config.json", 'r', encoding='utf-8') as file:
        config = json.load(file)

    logging.config.dictConfig(config=config["logger"])
    logger = logging.getLogger(name=config["app"])

    db = Database(config=config)

    sxodim_parser = SxodimParser(logger=logger, db=db)

    try:
        logger.info(f"Parser started")
        await asyncio.gather(
            sxodim_parser.parse()
        )
    except Exception as err:
        logger.fatal(f"Parser failed with error {err}\nTRACEBACK: {traceback.format_exc()}")
    finally:
        await close_connections()


async def close_connections():
    await session.close()


if __name__ == '__main__':
    if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
    ):
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
    loop.close()

