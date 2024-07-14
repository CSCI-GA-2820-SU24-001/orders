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
import logging
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes
from .models import db


######################################################################
# GET INDEX
######################################################################

logger = logging.getLogger("flask.app")


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


@app.route("/")
def index():
    """Root URL response"""
    return (
        "This is the root for the Orders API which provides CRUD operations for orders",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/orders", methods=["GET"])
def list_all_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for order list")

    orders = []

    # Parse any arguments from the query string
    customer_id = request.args.get("customer_id")
    status_name = request.args.get("status_name")

    if customer_id:
        app.logger.info("Find by customer_id: %s", customer_id)
        orders = Order.find_by_customer_id(customer_id)
    elif status_name:
        app.logger.info("Find by status: %s", status_name)
        orders = Order.find_by_status(status_name)
    else:
        app.logger.info("Find all")
        orders = Order.all()

    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/orders", methods=["POST"])
def create_order():
    """This method creates an order item given the items and their quantities"""
    # This method creates an order item given the items and their quantities"""
    # Assume POST request json data to have keys:
    #    item_ids: int arr,
    #    quantities: int arr,
    #    customer ID: int
    data = request.json
    logger.info("*************DATA*********************")
    logger.info(request.json)

    order_obj = Order()

    if "customer_id" not in data.keys():
        return (jsonify("Request missing parameter 'customer_id'"), status.HTTP_400_BAD_REQUEST)
    if "shipping_address" not in data.keys():
        return (jsonify("Request missing parameter 'shipping_address'"), status.HTTP_400_BAD_REQUEST)

    order_obj.customer_id = int(data["customer_id"])
    order_obj.shipping_address = data["shipping_address"]
    order_obj.status = OrderStatus.CREATED
    order_obj.created_at = datetime.now()
    data["status"] = "CREATED"
    data["created_at"] = datetime.now()

    order_obj.create()

    logger.info("ORDER ID: ")
    order_obj.deserialize(data)

    for item in data["items"]:
        item["order_id"] = order_obj.id

    # Create a message to return
    # for item in data["items"]:
    #     new_item = Item(order=order_obj)
    #     new_item.deserialize(item)
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


@app.route("/orders/<int:order_id>", methods=["GET"])
def view_order(order_id: int):
    """Returns the details of a specific order

    Args:
        order_id (int): ID of the order
    """
    curr_order = Order.query.filter_by(id=int(order_id)).first()
    if curr_order is None:
        abort(status.HTTP_404_NOT_FOUND, description="Order not found")
    logger.info("Returning order details:")
    logger.info("**********ORDER DETAILS***********")
    logger.info(jsonify(curr_order.serialize()))
    return jsonify(curr_order.serialize()), status.HTTP_200_OK


######################################################################
#  UPDATE IN ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """Update the order"""
    data = request.json
    curr_order = Order.query.filter_by(id=order_id).first()

    if not curr_order:
        abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

    if curr_order.status != OrderStatus.CREATED:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Order ID {order_id} cannot be updated in its current status",
        )

    logger.info("*************EXISTING ORDER DATA*********************")
    logger.info(curr_order.serialize())

    if "shipping_address" in data:
        curr_order.shipping_address = data["shipping_address"]

    if "status" in data:
        new_status = data.get("status")
        if new_status not in [status.name for status in OrderStatus]:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid status provided")

        new_status_enum = OrderStatus[new_status]
        valid_transitions = {
            OrderStatus.CREATED: [OrderStatus.PROCESSING],
            OrderStatus.PROCESSING: [OrderStatus.COMPLETED],
            OrderStatus.COMPLETED: [],
        }

        if new_status_enum not in valid_transitions[curr_order.status]:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Order ID {order_id} cannot be updated to {new_status}",
            )

        curr_order.status = new_status_enum

    curr_order.updated_at = datetime.now()
    curr_order.update()

    logger.info("**************UPDATED ORDER DATA************")
    logger.info(curr_order.serialize())

    return jsonify(curr_order.serialize()), status.HTTP_200_OK


######################################################################
#  DELETE ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """Delete an order"""
    logger.info("Deleting order with ID: %s", order_id)

    curr_order = Order.query.filter_by(id=order_id).first()

    if curr_order.status != OrderStatus.CREATED:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Order {order_id} cannot be deleted in its current status",
        )

    logger.info("*************ORDER TO DELETE*********************")
    logger.info(curr_order.serialize())

    curr_order.delete()

    logger.info("Order deleted successfully")

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  View a single item in an order
######################################################################


@app.route("/orders/<int:order_id>/item/<int:item_id>", methods=["GET"])
def view_item(order_id: int, item_id: int):
    """Returns the details of an item in an order

    Args:
        order_id (int): ID of the order
        item_id (int): ID of the item in the order

    """
    req_item = Item.query.filter_by(order_id=int(order_id), id=int(item_id)).first()
    if req_item is None:
        abort(status.HTTP_404_NOT_FOUND, description="Item not found")
    logger.info("Returning item details:")
    logger.info("**********ITEM DETAILS***********")
    logger.info(jsonify(req_item.serialize()))

    return jsonify(req_item.serialize()), status.HTTP_200_OK


######################################################################
#  UPDATE AN ITEM IN THE ORDER
######################################################################


@app.route("/orders/<int:order_id>/item/<int:item_id>", methods=["PUT"])
def update_item(order_id: int, item_id: int):
    """Update an item in the order"""
    logger.info("Updating item with ID: %s in order with ID: %s", item_id, order_id)

    data = request.json
    order = Order.query.filter_by(id=order_id).first()

    if order is None:
        abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

    if order.status != OrderStatus.CREATED:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Order ID {order_id} cannot be updated in its current status",
        )

    item = Item.query.filter_by(order_id=order_id, id=item_id).first()

    if item is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item ID {item_id} not found in Order ID {order_id}",
        )

    logger.info("*************EXISTING ITEM DATA*********************")
    logger.info(item.serialize())

    if "quantity" in data:
        item.quantity = data["quantity"]
    if "price" in data:
        item.price = data["price"]

    item.updated_at = datetime.now()
    item.update()

    logger.info("**************UPDATED ITEM DATA************")
    logger.info(item.serialize())

    message = item.serialize()
    return jsonify(message), status.HTTP_200_OK


@app.route("/orders/<int:order_id>/item/<int:item_id>", methods=["DELETE"])
def delete_item_from_order(order_id: int, item_id: int):
    """Delete an item from the order

    Args:
        order_id (int): ID of the order
        item_id (int): ID of the item in the order

    """
    order_del = Order.query.filter_by(id=int(order_id)).first()
    if order_del is None:
        abort(status.HTTP_404_NOT_FOUND, description="Order not found")

    item_del = Item.query.filter_by(id=int(item_id), order_id=int(order_del.id)).first()
    if item_del is None:
        return jsonify({"message": "Item does not exist"}), status.HTTP_404_NOT_FOUND
    db.session.delete(item_del)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"}), status.HTTP_204_NO_CONTENT


######################################################################
#  Add/Create a new item
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_item_to_order(order_id):
    """
    Add a new item to an order.
    """
    app.logger.info("Request to add an item to order %s", order_id)

    order = Order.query.get(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    item_data = request.get_json()
    if not item_data:
        abort(status.HTTP_400_BAD_REQUEST, "No data provided")

    try:
        new_item = Item(
            order_id=order.id,
            product_id=item_data["product_id"],
            product_description=item_data["product_description"],
            quantity=item_data["quantity"],
            price=item_data["price"],
        )
        db.session.add(new_item)
        db.session.commit()
    except KeyError as e:
        abort(status.HTTP_400_BAD_REQUEST, f"Missing field: {str(e)}")
    except DataValidationError as e:
        db.session.rollback()
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating item: {str(e)}")

    response_data = new_item.serialize()

    location_url = url_for(
        "view_item", order_id=order.id, item_id=new_item.id, _external=True
    )

    return jsonify(response_data), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  LIST ITEMS IN AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items_in_order(order_id: int):
    """Returns the list of items in an order"""
    order = Order.query.filter_by(id=order_id).first()
    if order is None:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")

    items = Item.query.filter_by(order_id=order_id).all()
    items_list = [item.serialize() for item in items]

    logger.info("Returning %d items for order ID %d", len(items_list), order_id)

    return jsonify(items_list), status.HTTP_200_OK
