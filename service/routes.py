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

from flask_restx import fields, reqparse, Resource

# pylint: disable=cyclic-import
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes
from .models import db
from . import api

logger = logging.getLogger("flask.app")


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")
    # return (
    #     {
    #         "general info": "This is the root for the Orders API",
    #         "endpoints": [
    #             {
    #                 "Endpoint": "list_all_orders",
    #                 "method": "GET",
    #                 "description": "Returns all of the Orders",
    #             },
    #             {
    #                 "Endpoint": "create_order",
    #                 "method": "POST",
    #                 "description": "Create an order item given the items and their quantities",
    #             },
    #             {
    #                 "Endpoint": "add_item_to_order",
    #                 "method": "POST",
    #                 "description": "Add an item to order",
    #             },
    #             {
    #                 "Endpoint": "change_status",
    #                 "method": "PUT",
    #                 "description": "Change the status of an order",
    #             },
    #             {
    #                 "Endpoint": "delete_item_from_order",
    #                 "method": "DELETE",
    #                 "description": "Delete an item from an order",
    #             },
    #             {
    #                 "Endpoint": "delete_order",
    #                 "method": "DELETE",
    #                 "description": "Delete an item from an order",
    #             },
    #             {
    #                 "Endpoint": "health_check",
    #                 "method": "GET",
    #                 "description": "Check health of API",
    #             },
    #             {
    #                 "Endpoint": "index",
    #                 "method": "GET",
    #                 "description": "Get the root URL and information about the orders API",
    #             },
    #             {
    #                 "Endpoint": "list_items_in_order",
    #                 "method": "GET",
    #                 "description": "List all items in an order",
    #             },
    #             {
    #                 "Endpoint": "update_item",
    #                 "method": "PUT",
    #                 "description": "Update an item in an order",
    #             },
    #             {
    #                 "Endpoint": "update_order",
    #                 "method": "PUT",
    #                 "description": "Update an order",
    #             },
    #             {
    #                 "Endpoint": "view_item",
    #                 "method": "GET",
    #                 "description": "View an item",
    #             },
    #             {
    #                 "Endpoint": "view_order",
    #                 "method": "GET",
    #                 "description": "View an order",
    #             },
    #         ],
    #     },
    #     status.HTTP_200_OK,
    # )


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
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
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
#  PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """Handles all interactions with collections of Orders"""

    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    @api.response(200, "Success")
    @api.response(400, "Bad Request")
    def get(self):
        """Returns all of the Orders"""
        app.logger.info("Request for order list")

        orders = []
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

        app.logger.info("Returning %d orders", len(orders))
        return orders, status.HTTP_200_OK

    @api.doc("create_order")
    @api.expect(order_create_model)
    @api.marshal_with(order_model, code=status.HTTP_201_CREATED)
    @api.response(201, "Order created successfully")
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Creates a new Order record in the database"""
        data = request.json
        logger.info("Received data: %s", data)

        order_obj = Order(
            customer_id=data["customer_id"],
            shipping_address=data["shipping_address"],
            status=OrderStatus[data["status"]],
            created_at=datetime.now(),
        )

        order_obj.create()
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

        logger.info("Created order: %s", order_obj.serialize())
        return order_obj.serialize(), status.HTTP_201_CREATED


######################################################################
#  PATH: /orders/{order_id}
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):

    @api.doc("get_order")
    @api.marshal_with(order_model)
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    def get(self, order_id):
        """Returns the Order with a given id number"""
        curr_order = Order.query.filter_by(id=order_id).first()
        if curr_order is None:
            abort(status.HTTP_404_NOT_FOUND, description="Order not found")
        return curr_order.serialize(), status.HTTP_200_OK

    @api.doc("update_order")
    @api.expect(order_create_model)
    @api.marshal_with(order_model)
    @api.response(200, "Order updated successfully")
    @api.response(400, "Bad Request")
    @api.response(404, "Order not found")
    def put(self, order_id):
        """Updates an Order record in the database"""
        data = request.json
        curr_order = Order.query.filter_by(id=order_id).first()

        if not curr_order:
            abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

        if curr_order.status != OrderStatus.CREATED:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Order ID {order_id} cannot be updated in its current status",
            )

        if "shipping_address" in data:
            curr_order.shipping_address = data["shipping_address"]
        if "status" in data:
            new_status = OrderStatus[data.get("status")]
            if new_status not in [status.name for status in OrderStatus]:
                abort(status.HTTP_400_BAD_REQUEST, "Invalid status provided")
        #            curr_order.status = new_status

        curr_order.updated_at = datetime.now()
        curr_order.update()

        return curr_order.serialize(), status.HTTP_200_OK

    @api.doc("delete_order")
    @api.response(204, "Order deleted successfully")
    @api.response(404, "Order not found")
    def delete(self, order_id):
        """Deletes an Order record in the database"""
        curr_order = Order.query.filter_by(id=order_id).first()
        if curr_order:
            curr_order.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id}/status
######################################################################
@api.route("/orders/<int:order_id>/status")
@api.param("order_id", "The Order identifier")
class OrderStatusResource(Resource):
    """Change the status of an order"""

    @api.doc("change_status")
    @api.expect(status_update_model)
    @api.marshal_with(order_model)
    @api.response(200, "Order status updated successfully")
    @api.response(400, "Bad Request")
    @api.response(404, "Order not found")
    def put(self, order_id):
        """Change the status of an order"""
        data = request.json
        curr_order = Order.query.filter_by(id=order_id).first()

        if not curr_order:
            abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

        new_status = data.get("status")
        if new_status not in [status.name for status in OrderStatus]:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid status provided")

        new_status_enum = OrderStatus[new_status]
        valid_transitions = {
            OrderStatus.CREATED: [OrderStatus.CREATED, OrderStatus.PROCESSING],
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

        return curr_order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):

    @api.doc("get_item")
    @api.marshal_with(item_model)
    @api.response(200, "Success")
    @api.response(404, "Item not found")
    def get(self, order_id, item_id):
        """Returns the Item with a given id number"""
        req_item = Item.query.filter_by(order_id=order_id, id=item_id).first()
        #    if req_item is None:
        #        abort(status.HTTP_404_NOT_FOUND, description="Item not found")
        return req_item.serialize(), status.HTTP_200_OK

    @api.doc("update_item")
    @api.expect(item_create_model)
    @api.marshal_with(item_model)
    @api.response(200, "Item updated successfully")
    @api.response(400, "Bad Request")
    @api.response(404, "Item not found")
    def put(self, order_id, item_id):
        """Updates an Item record in the database"""
        # data = request.json
        # order = Order.query.filter_by(id=order_id).first()

        # if order is None:
        #     abort(status.HTTP_404_NOT_FOUND, f"Order ID {order_id} not found")

        # if order.status != OrderStatus.CREATED:
        #     abort(
        #         status.HTTP_400_BAD_REQUEST,
        #         f"Order ID {order_id} cannot be updated in its current status",
        #     )

        # item = Item.query.filter_by(order_id=order_id, id=item_id).first()

        # if item is None:
        #     abort(
        #         status.HTTP_404_NOT_FOUND,
        #         f"Item ID {item_id} not found in Order ID {order_id}",
        #     )

        # if "quantity" in data:
        #     item.quantity = data["quantity"]
        # if "price" in data:
        #     item.price = data["price"]

        # item.updated_at = datetime.now()
        # item.update()

        # return item.serialize(), status.HTTP_200_OK

    @api.doc("delete_item")
    @api.response(204, "Item deleted successfully")
    @api.response(404, "Item not found")
    def delete(self, order_id, item_id):
        """Deletes an Item record in the database"""
        item_del = Item.query.filter_by(id=item_id, order_id=order_id).first()
        if item_del is None:
            return (
                jsonify({"message": "Item does not exist"}),
                status.HTTP_404_NOT_FOUND,
            )
        item_del.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id}/items
######################################################################
@api.route("/orders/<int:order_id>/items", strict_slashes=False)
@api.param("order_id", "The Order identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Items"""

    @api.doc("list_items")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    @api.response(200, "Success")
    @api.response(404, "Order not found")
    def get(self, order_id):
        """Returns a list of all the Items in an Order"""
        order = Order.query.filter_by(id=order_id).first()
        #      if order is None:
        #         abort(status.HTTP_404_NOT_FOUND, "Order not found")

        query = Item.query.filter_by(order_id=order_id)
        product_id = request.args.get("product_id")
        quantity = request.args.get("quantity")
        price = request.args.get("price")

        if product_id:
            query = query.filter_by(product_id=product_id)
        if quantity:
            query = query.filter_by(quantity=int(quantity))
        if price:
            query = query.filter_by(price=float(price))

        items = query.all()
        return items, status.HTTP_200_OK

    @api.doc("add_item")
    @api.expect(item_create_model)
    @api.marshal_with(item_model, code=status.HTTP_201_CREATED)
    @api.response(201, "Item created successfully")
    @api.response(400, "Bad Request")
    @api.response(404, "Order not found")
    @api.response(500, "Internal Server Error")
    def post(self, order_id):
        """Creates a new Item record in the database"""
        app.logger.info("Request to add an item to order %s", order_id)

        order = Order.query.get(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        item_data = request.get_json()
        #       if not item_data:
        #           abort(status.HTTP_400_BAD_REQUEST, "No data provided")

        new_item = Item(
            order_id=order.id,
            product_id=item_data["product_id"],
            product_description=item_data["product_description"],
            quantity=item_data["quantity"],
            price=item_data["price"],
        )
        db.session.add(new_item)
        db.session.commit()

        location_url = url_for(
            "item_resource", order_id=order.id, item_id=new_item.id, _external=True
        )
        return new_item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}
