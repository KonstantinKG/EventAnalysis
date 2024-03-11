import asyncio
import json
import logging.config
import sys

import aiohttp_cors
from aiohttp import web
from aiohttp_swagger import setup_swagger

from controllers import EventAnalysisController
from helpers import Database

with open("config.json", 'r', encoding='utf-8') as file:
    config = json.load(file)

logging.config.dictConfig(config=config["logger"])
logger = logging.getLogger(name=config["app"])

database = Database(config=config)

event_analysis_controller = EventAnalysisController(
    config=config,
    logger=logger,
    db=database
)

app = web.Application()


async def get(request):
    response = await event_analysis_controller.get(request=request)
    return web.json_response(response)


async def all(request):
    response = await event_analysis_controller.all(request=request)
    return web.json_response(response)


async def get_filters(request):
    response = await event_analysis_controller.get_filters(request=request)
    return web.json_response(response)


async def get_prices_dates(request):
    response = await event_analysis_controller.get_available_dates(request=request)
    return web.json_response(response)


async def get_prices(request):
    response = await event_analysis_controller.get_prices(request=request)
    return web.json_response(response)


app.router.add_get('/get', get)
app.router.add_get('/all', all)
app.router.add_get('/get/filters', get_filters)
app.router.add_get('/get/prices/dates', get_prices_dates)
app.router.add_get('/get/prices', get_prices)

setup_swagger(app, swagger_url="/api/documentation", swagger_from_file="swagger.yaml", ui_version=3)


cors = aiohttp_cors.setup(
    app=app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
    ):
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)

    logger.info(f"Running server on {config['host']}:{config['port']}")
    web.run_app(
        app=app,
        host=config['host'],
        port=config['port']
    )
