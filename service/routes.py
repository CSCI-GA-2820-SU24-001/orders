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
Orders Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Orders
"""
from datetime import datetime
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes
import logging


######################################################################
# GET INDEX
######################################################################

logger = logging.getLogger("flask.app")


@app.route("/orders")
def index():
    """Root URL response"""
    return (
        "This is the root for the Orders API which provides CRUD operations for orders",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

@app.route("/orders", methods=['GET', 'POST', 'PUT', 'DELETE'])
def order():

    if request.method == 'POST':
        """ This method creates an order item given the items and their quantities """
        """ Assume POST request json data to have keys:
            item_ids: int arr,
            quantities: int arr,
            customer ID: int
        """
    data = request.json
    logger.info("*************DATA*********************")
    logger.info(request.json)

    order_obj = Order()

    order_obj.customer_id = int(data["customer_id"])
    order_obj.shipping_address = data["shipping_address"]
    order_obj.status = OrderStatus.CREATED
    order_obj.created_at = datetime.now()

    order_obj.create()

    logger.info("ORDER ID: ")
    order_obj.deserialize(request.get_json())

    for item in data["items"]:
        item["order_id"] = order_obj.id

    # Create a message to return
    for item in data["items"]:
        new_item = Item(order=order_obj)
        new_item.deserialize(item)
        # new_item.order_id = item["order_id"]
        # new_item.product_id = item["id"]
        # new_item.quantity = item["quantity"]
        # new_item.product_description = item["product_description"]
        # new_item.price = item["price"]
        # new_item.order_id = order_obj.id
        # new_item.update()
    logger.info("**************ACTUAL DATA************")
    logger.info(order_obj.items)
    message = order_obj.serialize()
    return (jsonify(message), status.HTTP_201_CREATED)

######################################################################
#  LIST ALL ORDERS
######################################################################


@app.route("/orders/customer/<int:customer_id>", methods=["GET"])
def list_orders(customer_id):
    """Returns all of the orders"""
    logger.info("Retrieving orders for customer id: %s", customer_id)

    customer_exists = Order.query.filter_by(customer_id=str(customer_id)).first() is not None
    # Check if can't find customer
    if not customer_exists:
        abort(status.HTTP_404_NOT_FOUND, description="Customer not found")

    orders = Order.query.filter_by(customer_id=str(customer_id)).all()
    
    order_list = [order.serialize() for order in orders]
    return jsonify(order_list), status.HTTP_200_OK


@app.route("/orders/<int:order_id>", methods=["GET"])
def view_order(order_id: int):
    """Returns the details of a specific order

    Args:
        order_id (int): ID of the order
    """
    curr_order = Order.query.filter_by(id=int(order_id)).first()
    if curr_order is None:
        abort(status.HTTP_404_NOT_FOUND, description="Order not found")
    print("**********ORDER DETAILS***********")
    print(jsonify(curr_order.serialize()))
    return jsonify(curr_order.serialize()), status.HTTP_200_OK


