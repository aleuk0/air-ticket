from typing import AsyncIterator
import traceback
import argparse
import os

from aiohttp import web, ClientSession

from views import create_new_reserve, orders, bags

import logging
logging.basicConfig(filename='info.log', encoding='utf-8', level=logging.INFO)
log = logging.getLogger(__name__)


async def init_app(args) -> web.Application:
    app = web.Application(middlewares=[error_middleware], logger=log)

    app['orders_url'] = args.orders_url
    app['bags_url'] = args.bags_url

    app.cleanup_ctx.append(init_aiohttp_session)

    routes = [
        web.post('/applications', create_new_reserve),
        web.get('/orders', orders),
        web.put('/bags', bags),
    ]
    app.add_routes(routes)

    return app


async def init_aiohttp_session(app: web.Application) -> AsyncIterator[None]:
    async with ClientSession(raise_for_status=True) as session:
        app['session'] = session
        yield


@web.middleware
async def error_middleware(req: web.Request, handler):
    try:
        return await handler(req)
    except Exception as e:
        log.warning(e)
        return web.json_response(
            {
                'error': e.__class__.__name__,
                # 'error_info': traceback.format_exc(),
            },
            status=500,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orders_url',
                        default=os.environ.get('ORDERS_URL', 'http://127.0.0.1:8080/orders'))
    parser.add_argument('--bags_url',
                        default=os.environ.get('BAGS_URL', 'http://127.0.0.1:8080/bags'))
    args = parser.parse_args()

    web.run_app(init_app(args), access_log=log)


if __name__ == '__main__':
    main()
