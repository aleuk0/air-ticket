from dataclasses import dataclass
import json
import re
from typing import List

from aiohttp import web

import logging
log = logging.getLogger(__name__)


class Reserve:
    """ Working with whole reserving process """

    def __init__(self, order) -> None:
        self.order: Order = order
        self.bags: List[Bag] = []
        self.success: bool = False

    def get_bags_from_order(self):
        if not self.order or not self.order.raw_order:
            raise Exception(
                f"Reserve number {self.order.number}, passengerId {self.order.passengerId} "
                f"Incoplete Order"
            )
        order_main_part = self.order.raw_order['ancillariesPricings'][0]['baggagePricings']
        for route in order_main_part:
            baggages = []
            for baggage in route.get('baggages'):
                if baggage.get('equipmentType') == 'ski':
                    baggages.append(baggage['id'])
            if baggages:
                for passengerId in route.get('passengerIds'):
                    self.bags.append(Bag(passengerId, route['routeId'], baggages))
        if not self.bags:
            raise Exception(
                f"Reserve number {self.order.number}, passengerId {self.order.passengerId} "
                f"No bags was found in order"
            )
        else:
            log.info(
                f"Reserve number {self.order.number}, passengerId {self.order.passengerId} "
                f"{len(self.bags)} bags successfully found: "
                f"{self._get_bags_representation()}"
            )

    async def send_bags_for_update(self, request: web.Request):
        data = json.dumps({'baggageSelections': self._get_bags_representation()})

        async with request.app['session'].put(request.app['bags_url'],
                                              raise_for_status=True,
                                              data=data) as resp:
            if resp.status >= 400:
                raise Exception(
                    f"Reserve number {self.order.number}, passengerId {self.order.passengerId} "
                    f"Error from bags service, data: {data}"
                )
            result = await resp.json()
            if result.get('shoppingCart') == None and result.get('error'):
                raise Exception(
                    f"Reserve number {self.order.number}, passengerId {self.order.passengerId} "
                    f"Error result from bags service: {result['error']}, data: {data}"
                )
            self.success = True

    def _get_bags_representation(self):
        return [bag.get_representation() for bag in self.bags]


@dataclass
class Order:
    """ Working with Order and order service """

    number: str
    passengerId: str
    raw_order: str

    def __init__(self, number, passengerId) -> 'Order':
        if not (
            re.match("^[A-Za-z0-9]{6}$", number)
            and re.match("^[A-Za-z]*$", passengerId)
        ):
            raise Exception(
                f'Wrong format of input data, number: {number}, passengerId: {passengerId}'
            )
        self.number = number
        self.passengerId = passengerId

    async def get_data(self, request: web.Request):
        params = {'number': self.number, 'passengerId': self.passengerId}
        async with request.app['session'].get(request.app['orders_url'],
                                              raise_for_status=False,
                                              params=params) as resp:
            if resp.status >= 400:
                raise Exception(
                    f"Reserve number {self.number}, passengerId {self.passengerId} "
                    f"Error from order service, params: {params}"
                )
            self.raw_order = await resp.json()
            log.info(
                f"Reserve number {self.number}, passengerId {self.passengerId} "
                f"order from service received: "
                f"{self.raw_order}"
            )


@dataclass
class Bag:
    """ Storing bags for request """

    passengerId: str
    routeId: str
    baggageIds: List[str]

    def get_representation(self):
        result = self.__dict__
        result.update({'redemption': False})
        return result
