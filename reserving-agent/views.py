from aiohttp import web

from models import Reserve, Order
from responses import Responses

import logging
log = logging.getLogger(__name__)


async def create_new_reserve(request: web.Request):
    """ main function to create reserve for ski """

    try:
        data = await request.json()
        order = Order(data['number'], data['passengerId'])
        await order.get_data(request)
        reserve = Reserve(order)
        reserve.get_bags_from_order()
        await reserve.send_bags_for_update(request)
        if reserve.success:
            log.info(
                f"Reserve number {data['number']}, passengerId {data['passengerId']} "
                f"successfully completed"
            )
    except Exception as e:
        log.warning(e)
        raise web.HTTPBadRequest()
    else:
        return web.json_response({'success': True}, status=200)


async def orders(request: web.Request):
    """ instead of orders service """
    return web.json_response(Responses.ORDER_RESPONSE)


async def bags(request: web.Request):
    """ instead of bags service """
    data = await request.json()
    return web.json_response(Responses.BAGS_RESPONSE_OK)
