######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Steps

Steps file for Order.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following orders")
def step_impl(context):
    """Delete all Orders and load new ones"""

    # Get a list all of the orders
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for order in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{order['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new orders
    for row in context.table:
        payload = {
            "items": [],
            "customer_id": row["customer_id"],
            "shipping_address": row["shipping_address"],
            "created_at": row["created_at"],
            "status": row["status"],
        }
        payload["items"].append(
            {
                "product_id": 1,
                "order_id": 0,
                "quantity": 2,
                "price": 23.4,
                "product_description": "Glucose",
            }
        )
        payload["items"].append(
            {
                "product_id": 2,
                "order_id": 0,
                "quantity": 1,
                "price": 10.0,
                "product_description": "Candy",
            }
        )
        # print(payload)
        context.resp = requests.post(
            rest_endpoint,
            json=payload,
            timeout=WAIT_TIMEOUT,
        )
        data = context.resp.json()
        context.valid_order_id = data["order_id"]
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the following items")
def step_impl(context):
    """Delete all items and load new ones"""

    # Get a list all of the orders
    # rest_endpoint = f"{context.base_url}/orders"
    # context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    # expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # # and delete them one by one
    # for order in context.resp.json():
    #     for item in order["items"]:
    #         if item:
    #             print("Inside item")
    #             context.resp = requests.delete(
    #                 f"{rest_endpoint}/{order['id']}/item/{item['id']}",
    #                 timeout=WAIT_TIMEOUT,
    #             )
    #             expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new items
    # for row in context.table:
    #     payload = {
    #         "order_id": int(row["order_id"]),
    #         "product_id": int(row["product_id"]),
    #         "price": float(row["price"]),
    #         "quantity": int(row["quantity"]),
    #         "product_description": row["product_description"],
    #     }
    #     context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
    #     expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
