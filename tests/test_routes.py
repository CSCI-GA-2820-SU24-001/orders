"""
TestYourResourceModel API Service Test Suite
"""

import os
import random
from datetime import datetime
import logging
from unittest import TestCase
from wsgi import app

from service.common import status
from service.models import db, Order, Item

from .factories import ItemFactory

logger = logging.getLogger("flask.app")


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_create(self):
        """
        It should call the method to create an order and return a 201 status code
        """
        request = {
            "items": [],
            "customer_id": random.randint(0, 10000),
            "shipping_address": "726 Broadway, NY 10003",
            "created_at": int(datetime.timestamp(datetime.now())),
            "status": "CREATED",
        }

        request["items"].append(
            {
                "product_id": 1,
                "order_id": 0,
                "quantity": 2,
                "price": 23.4,
                "product_description": "Glucose",
            }
        )

        logger.info("***************** SENT DATA *******************")

        logger.info(request["items"])
        response = self.client.post(
            BASE_URL, json=request, content_type="application/json"
        )
        order_data = response.get_json()

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            int(order_data["customer_id"]),
            int(request["customer_id"]),
            "Customer ID does not match",
        )
        self.assertEqual(
            order_data["items"][0]["price"],
            request["items"][-1]["price"],
            "Item price does not match",
        )
        self.assertEqual(
            order_data["items"][0]["quantity"],
            request["items"][-1]["quantity"],
            "Item quantity does not match",
        )
        self.assertEqual(
            order_data["items"][0]["product_description"],
            request["items"][-1]["product_description"],
            "Item description does not match",
        )

    def test_list_orders(self):
        """It should list orders"""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()

        order2 = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order2.create()

        response = self.client.get(
            f"{BASE_URL}/customer/{customer_id}", content_type="application/json"
        )
        order_list = response.get_json()

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(order_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_not_found(self):
        """It should check if customer doesn't exist"""
        non_existent_customer_id = random.randint(10001, 20000)
        response = self.client.get(
            f"{BASE_URL}/customer/{non_existent_customer_id}",
            content_type="application/json",
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_order(self):
        """It should view an order"""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()

        response = self.client.get(
            f"{BASE_URL}/{order1.id}", content_type="application/json"
        )
        order_view = response.get_json()

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(order_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_not_found(self):
        """It should check if order does not exist"""
        non_existent_order_id = random.randint(10001, 20000)
        response = self.client.get(
            f"{BASE_URL}/{non_existent_order_id}",
            content_type="application/json",
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_addr(self):
        """It should update an existing order"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # New shipping address data
        update_data = {"shipping_address": "1428 Elm St"}

        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )
        updated_order = response.get_json()

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(updated_order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            updated_order["shipping_address"], update_data["shipping_address"]
        )

    def test_update_order_addr_not_found(self):
        """It should check if it can't find order to update address"""
        # use non existent order
        non_existent_order_id = random.randint(10001, 20000)

        update_data = {"shipping_address": "1428 Elm St"}

        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{non_existent_order_id}",
            json=update_data,
            content_type="application/json",
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_addr_in_processing(self):
        """It should check if it's in PROCESSING status"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            # status not in CREATE
            status="PROCESSING",
        )
        order.create()

        update_data = {"shipping_address": "1428 Elm St"}

        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_addr_in_completed(self):
        """It should check if it's in COMPLETED status"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            # status not in CREATE
            status="COMPLETED",
        )
        order.create()

        update_data = {"shipping_address": "1428 Elm St"}

        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status(self):
        """It should update the order status"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # New status data
        update_data = {"status": "PROCESSING"}

        logger.info("***************** SENT STATUS DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}/status",
            json=update_data,
            content_type="application/json",
        )
        updated_order = response.get_json()

        logger.info("***************** RECEIVED STATUS DATA *******************")
        logger.info(updated_order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_order["status"], update_data["status"])

    def test_update_order_status_skip(self):
        """It should not allow updating the status from CREATED to COMPLETED"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # Invalid status transition data
        update_data = {"status": "COMPLETED"}

        logger.info("***************** SENT INVALID STATUS DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}/status",
            json=update_data,
            content_type="application/json",
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.status_code)
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_non_existent(self):
        """It should not allow updating to a non-existent status"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        update_data = {"status": "HAPPY"}

        logger.info(
            "***************** SENT NON-EXISTENT STATUS DATA *******************"
        )
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}/status",
            json=update_data,
            content_type="application/json",
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.status_code)
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_not_found(self):
        """It should check if it can't find order to update status"""
        non_existent_order_id = random.randint(10001, 20000)

        update_data = {"status": "PROCESSING"}

        logger.info(
            "***************** SENT STATUS DATA FOR NON-EXISTENT ORDER *******************"
        )
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{non_existent_order_id}/status",
            json=update_data,
            content_type="application/json",
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.status_code)
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        """It should delete an existing order"""
        customer_id = random.randint(0, 10000)
        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        response = self.client.delete(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )

        logger.info("***************** DELETE RESPONSE *******************")
        logger.info(response.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existent_order(self):
        """It should check if it's deleting a non-existent order"""
        non_existent_order_id = random.randint(10001, 20000)
        response = self.client.delete(
            f"{BASE_URL}/{non_existent_order_id}",
            content_type="application/json",
        )

        logger.info("***************** DELETE RESPONSE *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_in_processing(self):
        """It should not delete an order that is in PROCESSING status"""
        customer_id = random.randint(0, 10000)
        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="PROCESSING",
        )
        order.create()

        response = self.client.delete(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )

        logger.info("***************** DELETE RESPONSE *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order_in_completed(self):
        """It should not delete an order that is in COMPLETED status"""
        customer_id = random.randint(0, 10000)
        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="COMPLETED",
        )
        order.create()

        response = self.client.delete(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )

        logger.info("***************** DELETE RESPONSE *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_item(self):
        """It should view an item in an order"""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()
        item1 = ItemFactory(order=order1)
        item1.create()
        response = self.client.get(
            f"{BASE_URL}/{order1.id}/item/{item1.id}",
            content_type="application/json",
        )
        item_view = response.get_json()

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(item_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            f"{BASE_URL}/{order1.id}/item/502212",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_item_not_found(self):
        """It should check if order does not exist"""
        non_existent_order_id = random.randint(10001, 20000)
        non_existent_item_id = random.randint(10001, 20000)

        response = self.client.get(
            f"{BASE_URL}/{non_existent_order_id}item/{non_existent_item_id}",
            content_type="application/json",
        )

        logger.info("***************** RECEIVED DATA *******************")
        logger.info(response.get_json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item(self):
        """It should delete an item in an order"""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()
        item1 = ItemFactory(order=order1)
        item1.create()
        response = self.client.delete(
            f"{BASE_URL}/{order1.id}/item/{item1.id}",
            content_type="application/json",
        )
        # print(response.data)
        # item_view = response.get_json()

        # logger.info("***************** RECEIVED DATA *******************")
        # logger.info(item_view)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(
            f"{BASE_URL}/70210/item/{item1.id}",
            content_type="application/json",
        )
        print("RESPONSE: ", response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            f"{BASE_URL}/{order1.id}/item/12434353",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item(self):
        """It should update the item in order"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        item = Item(
            order_id=order.id,
            product_id=1,
            quantity=2,
            price=23.4,
            product_description="Apple",
        )
        item.create()

        # update the quantities and total price
        update_data = {
            "quantity": 5,
            "price": 30.0,
        }

        logger.info("***************** SENT ITEM DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}/item/{item.id}",
            json=update_data,
            content_type="application/json",
        )

        updated_item = response.get_json()

        logger.info("***************** RECEIVED ITEM DATA *******************")
        logger.info(updated_item)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_item["quantity"], update_data["quantity"])
        self.assertEqual(updated_item["price"], update_data["price"])

    def test_update_item_order_not_found(self):
        """It should check if it can't find order"""
        non_existent_order_id = random.randint(10001, 20000)
        item_id = random.randint(1, 100)

        update_data = {
            "product_id": 2,
            "quantity": 5,
            "price": 30.0,
        }

        response = self.client.put(
            f"{BASE_URL}/{non_existent_order_id}/item/{item_id}",
            json=update_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Order ID {non_existent_order_id} not found",
            response.get_json()["message"],
        )

    def test_update_item_not_found(self):
        """It should check if it can't find item"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # Create non exist item id
        non_existent_item_id = random.randint(10001, 20000)

        update_data = {
            "product_id": 2,
            "quantity": 5,
            "price": 30.0,
        }

        response = self.client.put(
            f"{BASE_URL}/{order.id}/item/{non_existent_item_id}",
            json=update_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Item ID {non_existent_item_id} not found in Order ID {order.id}",
            response.get_json()["message"],
        )

    def test_update_item_not_created(self):
        """It should check if the order status is not CREATED"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="1428 Elm St",
            created_at=datetime.now(),
            # non CREATED
            status="PROCESSING",
        )
        order.create()

        item = Item(
            order_id=order.id,
            product_id=1,
            quantity=2,
            price=23.4,
            product_description="Apple",
        )
        item.create()

        update_data = {
            "product_id": 2,
            "quantity": 5,
            "price": 30.0,
        }

        response = self.client.put(
            f"{BASE_URL}/{order.id}/item/{item.id}",
            json=update_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"Order ID {order.id} cannot be updated in its current status",
            response.get_json()["message"],
        )
