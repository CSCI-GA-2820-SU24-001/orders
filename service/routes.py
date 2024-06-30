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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/orders")
def index():
    """Root URL response"""
    return (
        "This is the root for the Orders API. The REST API provides the functionality to create, update, delete and update orders and order items",
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
            item IDs: int arr, 
            quantities: int arr, 
            prices: float arr, 
            customer ID: int
        """
    data = request.json

    order = OrderFactory()
    for item, quant, price in zip(data["items"], data["quantities"], data["prices"]):
        new_item = ItemFactory(order=order)

    return (
        "This is the root for the Orders API. The REST API provides the functionality to create, update, delete and update orders and order items",
        status.HTTP_200_OK,
    )
