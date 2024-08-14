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
import logging
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application

# from flask_restx import Resource
from flask_restx import Resource, fields, reqparse

# pyl disable=cyclic-import
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes
from .models import db
from . import api

logger = logging.getLogger("flask.app")


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


# class TimestampDateFormat(fields.Raw):
#     """Use to convert timestamp into readable date time for Flask-RestX"""

#     def format(self, value):
#         return datetime.fromtimestamp(value)


@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
item_create_model = api.model(
    "ItemCreateModel",
    {
        "order_id": fields.Integer(
            required=True, description="The Order an Item is belonged to"
        ),
        "product_id": fields.Integer(
            required=True, description="The product an Item is belonged to"
        ),
        "product_description": fields.String(
            required=True, description="The description for the Item"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the Item ordered"
        ),
        "price": fields.Float(required=True, description="The unit price for the Item"),
    },
)

item_model = api.inherit(
    "ItemModel",
    item_create_model,
    {"id": fields.Integer(readOnly=True, description="The ID of the Item")},
)

order_create_model = api.model(
    "OrderCreateModel",
    {
        "customer_id": fields.Integer(
            required=True, description="The ID of the customer ordering the Order"
        ),
        "status": fields.String(
            enum=[e.name for e in OrderStatus], description="The status of the Order"
        ),
        "shipping_address": fields.String(
            required=True, description="The place where the Order is delivered to"
        ),
        "items": fields.List(
            fields.Nested(item_create_model),
            required=False,
            description="The items under the Order",
        ),
    },
)

order_model = api.inherit(
    "OrderModel",
    order_create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_at": fields.Date(),
        "updated_at": fields.Date(),
    },
)

status_update_model = api.model(
    "StatusUpdateModel",
    {
        "status": fields.String(
            required=True,
            description="The new status of the Order",
            enum=[e.name for e in OrderStatus],
        ),
    },
)

# query string arguments
item_args = reqparse.RequestParser()
item_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="List Items with a specific product id",
)
item_args.add_argument(
    "quantity",
    type=int,
    location="args",
    required=False,
    help="List Items with a specific quantity",
)
item_args.add_argument(
    "price",
    type=float,
    location="args",
    required=False,
    help="List Items with a specific price",
)

order_args = reqparse.RequestParser()
order_args.add_argument(
    "customer_id",
    type=int,
    location="args",
    required=False,
    help="List Orders from a specific customer",
)
order_args.add_argument(
    "status",
    type=str,
    location="args",
    required=False,
    help="List Orders with a specific Order status",
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  PATH: /orders/
######################################################################


@api.route("/orders")
class OrderCollection(Resource):
    """Allows listing or creating orders
    GET /orders - Returns all orders
    POST /orders - Create an order depending on the data in body
    """

    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """Returns all orders"""
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

        results = []
        for order in orders:
            res = order.serialize()
            # res["created_at"] = res["created_at"].timestamp()
            results.append(res)
            app.logger.info(res["id"])
        app.logger.info("Returning %d orders", len(results))

        return results, status.HTTP_200_OK

    @api.doc("create_order")
    @api.response(400, "Invalid data")
    @api.expect(order_create_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """This method creates an order given the items and their quantities"""
        data = request.json
        logger.info("*************DATA*********************")
        logger.info(request.json)

        order_obj = Order()

        if "customer_id" not in data.keys():
            return (
                "Request missing parameter 'customer_id'",
                status.HTTP_400_BAD_REQUEST,
            )
        if "shipping_address" not in data.keys():
            return (
                "Request missing parameter 'shipping_address'",
                status.HTTP_400_BAD_REQUEST,
            )

        order_obj.customer_id = int(data["customer_id"])
        order_obj.shipping_address = data["shipping_address"]
        order_obj.status = OrderStatus[data["status"]]

        order_obj.create()

        app.logger.info("ORDER ID: ")
        logger.error(order_obj.id)

        for item in data["items"]:
            new_item = Item(
                order_id=order_obj.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"],
                product_description=item["product_description"],
            )
            new_item.create()
            order_obj.items.append(new_item)
        order_obj.update()

        logger.info("**************ACTUAL DATA************")
        logger.info(order_obj.items)
        message = order_obj.serialize()
        # message["created_at"] = message["created_at"].timestamp()
        # print(message)
        return (message, status.HTTP_201_CREATED)


@api.route("/orders/<int:order_id>")
class OrderResource(Resource):
    """Class for the Order resource
    GET /orders/{order_id: int} - Return an order with order_id
    PUT /orders/{order_id: int} - Update an order with order_id
    DELETE /orders/{order_id: int} - Delete an order with order_id
    """

    @api.doc("get_order")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
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
        message = curr_order.serialize()
        # message["created_at"] = message["created_at"].timestamp()
        return message, status.HTTP_200_OK

    @api.doc("update_order")
    @api.response(400, "Invalid data")
    @api.response(404, "The order was not found")
    @api.expect(order_create_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update an order with the given ID"""
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
                OrderStatus.CREATED: [
                    OrderStatus.CREATED,
                    OrderStatus.PROCESSING,
                ],  # ADDED TO ALLOW UPDATING ORDER
                OrderStatus.PROCESSING: [OrderStatus.COMPLETED],
                OrderStatus.COMPLETED: [],
            }

            if new_status_enum not in valid_transitions[curr_order.status]:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"Order ID {order_id} cannot be updated to {new_status}",
                )

            curr_order.status = new_status_enum

        # curr_order.updated_at = datetime.now()
        curr_order.update()

        logger.info("**************UPDATED ORDER DATA************")
        logger.info(curr_order.serialize())
        message = curr_order.serialize()

        return message, status.HTTP_200_OK

    @api.doc("delete_order")
    @api.response(204, "Order deleted successfully")
    def delete(self, order_id):
        """Delete an order given an order ID"""
        logger.info("Deleting order with ID: %s", order_id)

        curr_order = Order.query.filter_by(id=order_id).first()

        if curr_order:
            logger.info("*************ORDER TO DELETE*********************")
            logger.info(curr_order.serialize())
            curr_order.delete()
            logger.info("Order deleted successfully")

        # Even if the order was not found, still return 204 No Content
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id:int}/items
######################################################################


@api.route("/orders/<int:order_id>/items")
class ItemCollection(Resource):
    """Class to handle Item collection operations"""

    @api.doc("create_item")
    @api.response(400, "Invalid Item data")
    @api.expect(item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Add a new item to an order.
        """
        app.logger.info("Request to add an item to order %s", order_id)

        order = Order.query.get(int(order_id))
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

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

        response_data = new_item.serialize()

        location_url = api.url_for(
            ItemResource, order_id=order.id, item_id=new_item.id, _external=True
        )

        return (
            response_data,
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )

    @api.doc("list_order_items")
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """Returns the list of items in an order"""
        logger.info("ORDER ID %d", order_id)

        order = Order.query.filter_by(id=int(order_id)).first()
        if order is None:
            abort(
                status.HTTP_404_NOT_FOUND,
                "Order not found for ID " + str(order_id) + " inside get",
            )

        # Add query parameters for filtering
        product_id = request.args.get("product_id")
        quantity = request.args.get("quantity")
        price = request.args.get("price")

        query = Item.query.filter_by(order_id=order_id)
        if product_id:
            query = query.filter_by(product_id=product_id)
        if quantity:
            query = query.filter_by(quantity=int(quantity))
        if price:
            query = query.filter_by(price=float(price))

        items = query.all()
        items_list = [item.serialize() for item in items]

        logger.info("Returning %d items for order ID %d", len(items_list), order_id)

        return items_list, status.HTTP_200_OK


######################################################################
#  PATH: /orders/{order_id:int}/item/{item_id:int}
######################################################################
@api.route("/orders/<int:order_id>/item/<int:item_id>")
@api.param("order_id", "The ID of the order (integer)")
@api.param("item_id", "The ID of the item in the order (integer)r")
class ItemResource(Resource):
    """
    ItemResource
    Handle operations on a single Item in an order
    GET /orders/{order_id}/item/{item_id} - Get the order item with the given id
    PUT /orders/{order_id}/item/{item_id} - Update the order item with the given id
    DELETE /orders/{order_id}/item/{item_id} - Delete the order item with the given id

    """

    @api.doc("get_order_item")
    @api.response(404, "Item Not Found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
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

        message = req_item.serialize()
        # message["created_at"] = message["created_at"].timestamp()

        return message, status.HTTP_200_OK

    @api.doc("update_order_item")
    @api.response(404, "Item not found")
    @api.response(400, "Invalid Item data")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Update an item in the order given order ID and item ID"""
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

        # item.updated_at = datetime.now()
        item.update()

        logger.info("**************UPDATED ITEM DATA************")
        logger.info(item.serialize())

        message = item.serialize()
        return message, status.HTTP_200_OK

    @api.doc("delete_order_item")
    @api.response(204, "Item deleted")
    def delete(self, order_id, item_id):
        """Delete an item from the order

        Args:
            order_id (int): ID of the order
            item_id (int): ID of the item in the order

        """
        order_del = Order.query.filter_by(id=int(order_id)).first()
        if order_del is None:
            abort(status.HTTP_404_NOT_FOUND, description="Order not found")

        item_del = Item.query.filter_by(
            id=int(item_id), order_id=int(order_del.id)
        ).first()
        if item_del is None:
            return (
                {"message": "Item does not exist"},
                status.HTTP_404_NOT_FOUND,
            )
        db.session.delete(item_del)
        db.session.commit()
        return (
            {"message": "Item deleted successfully"},
            status.HTTP_204_NO_CONTENT,
        )


######################################################################
#  PATH: /orders/{order_id:int}/status
######################################################################


@api.route("/orders/<int:order_id>/status")
@api.param("order_id", "The order identifier")
class OrderChangeStatus(Resource):
    """Change the status of an order"""

    @api.doc("change_order_status")
    @api.response(400, "Invalid status provided. Order status cannot be updated")
    @api.marshal_with(order_model)
    def put(self, order_id):
        """CHANGE ORDER STATUS

        Args:
            order_id (int): ID of the order

        Returns:
            JSON: order with changed status
        """
        data = request.json
        curr_order = Order.query.filter_by(id=order_id).first()

        if not curr_order:
            abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

        new_status = data.get("status")
        if new_status not in [status.name for status in OrderStatus]:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid status provided")

        new_status_enum = OrderStatus[new_status]
        valid_transitions = {
            OrderStatus.CREATED: [
                OrderStatus.CREATED,
                OrderStatus.PROCESSING,
            ],  # ADD TO ALLOW UPDATING ORDERS
            OrderStatus.PROCESSING: [OrderStatus.COMPLETED],
            OrderStatus.COMPLETED: [],
        }

        if new_status_enum not in valid_transitions[curr_order.status]:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Order ID {order_id} cannot be updated to {new_status}",
            )

        curr_order.status = new_status_enum
        curr_order.update()

        logger.info("**************UPDATED ORDER STATUS************")
        logger.info(curr_order.serialize())
        message = curr_order.serialize()

        return message, status.HTTP_200_OK
