"""
TestYourResourceModel API Service Test Suite
"""

import os
import random
from datetime import datetime
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from wsgi import app

from service.common import status
from service.models import db, Order, Item

from .factories import ItemFactory, OrderFactory

logger = logging.getLogger("flask.app")


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# pylint: disable=duplicate-code
class TestOrderAPIService(TestCase):
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

    ############################################################
    # Utility function to bulk create items and orders
    ############################################################
    def _create_orders(self, count: int = 1) -> list:
        """Factory method to create Orders in bulk"""
        orders = []
        for _ in range(count):
            test_order = OrderFactory()
            response = self.client.post(BASE_URL, json=test_order.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_orders = response.get_json()
            test_order.id = new_orders["id"]
            orders.append(test_order)
        return orders

    def _create_items(self, order, count: int = 1) -> list:
        """Factory method to create items in bulk for a given order"""
        items = []
        for _ in range(count):
            test_item = ItemFactory(order=order)
            response = self.client.post(
                f"{BASE_URL}/{order.id}/items", json=test_item.serialize()
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test item",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

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

    # ----------------------------------------------------------
    # TEST LIST AND QUERY
    # ----------------------------------------------------------
    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_by_customer_id(self):
        """It should Query Orders by customer id"""
        orders = self._create_orders(5)
        test_customer_id = orders[0].customer_id
        cust_count = len(
            [order for order in orders if order.customer_id == test_customer_id]
        )
        response = self.client.get(
            BASE_URL, query_string=f"customer_id={quote_plus(str(test_customer_id))}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), cust_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["customer_id"], str(test_customer_id))

    def test_query_by_status(self):
        """It should Query Orders by status"""
        orders = self._create_orders(5)
        test_status = orders[0].status
        status_count = len([order for order in orders if order.status == test_status])
        response = self.client.get(
            BASE_URL, query_string=f"status_name={test_status.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), status_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], test_status.name)

    # ----------------------------------------------------------
    # TEST CRUD
    # ----------------------------------------------------------
    def test_create(self):
        """
        It should call the method to create an order and return a 201 status code
        """
        request = {
            "items": [],
            "customer_id": random.randint(0, 10000),
            "shipping_address": "726 Broadway, NY 10003",
            "created_at": "Mon, 22 Jan 2024 17:00:52 GMT",
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

    def test_update_order(self):
        """It should update an existing order's shipping address and status"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # Update shipping address
        update_data_address = {"shipping_address": "1428 Elm St"}
        logger.info("***************** SENT ADDRESS DATA *******************")
        logger.info(update_data_address)

        response = self.client.put(
            f"{BASE_URL}/{order.id}",
            json=update_data_address,
            content_type="application/json",
        )
        updated_order = response.get_json()

        logger.info("***************** RECEIVED ADDRESS DATA *******************")
        logger.info(updated_order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            updated_order["shipping_address"], update_data_address["shipping_address"]
        )

        # Update order status
        update_data_status = {"status": "PROCESSING"}
        logger.info("***************** SENT STATUS DATA *******************")
        logger.info(update_data_status)

        response = self.client.put(
            f"{BASE_URL}/{order.id}",
            json=update_data_status,
            content_type="application/json",
        )
        updated_order = response.get_json()

        logger.info("***************** RECEIVED STATUS DATA *******************")
        logger.info(updated_order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_order["status"], update_data_status["status"])

    def test_update_order_not_found(self):
        """It should return 404 if the order to be updated is not found"""
        non_existent_order_id = random.randint(10001, 20000)

        update_data = {"shipping_address": "1428 Elm St"}
        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{non_existent_order_id}",
            json=update_data,
            content_type="application/json",
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_invalid_status(self):
        """It should return 400 if the order status transition is invalid"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        # Invalid status transition
        update_data = {"status": "COMPLETED"}
        logger.info("***************** SENT INVALID STATUS DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.status_code)
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_status_value(self):
        """It should return 400 if the new status is not a valid status value"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
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
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.status_code)
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_in_processing(self):
        """It should return 400 if the order is in PROCESSING status and update is attempted"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="PROCESSING",
        )
        order.create()

        update_data = {"shipping_address": "1428 Elm St"}
        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_in_completed(self):
        """It should return 400 if the order is in COMPLETED status and update is attempted"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="COMPLETED",
        )
        order.create()

        update_data = {"shipping_address": "1428 Elm St"}
        logger.info("***************** SENT DATA *******************")
        logger.info(update_data)

        response = self.client.put(
            f"{BASE_URL}/{order.id}", json=update_data, content_type="application/json"
        )

        logger.info("***************** RECEIVED RESPONSE *******************")
        logger.info(response.get_json())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_not_found(self):
        """It should return 404 if the order to update status is not found"""
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
            f"{BASE_URL}/{non_existent_order_id}/item/{non_existent_item_id}",
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

    def test_add_item(self):
        """It should Create a new Item"""
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

        # Perform POST request to create a new item
        response = self.client.post(
            f"{BASE_URL}/{order1.id}/items",
            json=item1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if 'Location' header is present
        location = response.headers.get("Location")
        self.assertIsNotNone(location)

        # Perform GET request to retrieve the newly created item
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the retrieved item matches the created item
        new_item = response.get_json()
        self.assertIsInstance(new_item, dict)
        self.assertEqual(str(new_item["product_id"]), str(item1.product_id))
        self.assertEqual(new_item["product_description"], item1.product_description)
        self.assertEqual(float(new_item["price"]), float(item1.price))
        self.assertEqual(int(new_item["quantity"]), item1.quantity)

    def test_add_item_sad_path_invalid_json(self):
        """Test adding a new item with invalid JSON data."""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()

        # Perform POST request with invalid JSON data
        response = self.client.post(
            f"{BASE_URL}/{order1.id}/items",
            data="Invalid JSON data",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_sad_path_missing_fields(self):
        """Test adding a new item with missing required fields."""
        customer_id = random.randint(0, 10000)
        order1 = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order1.create()

        # Create an item with missing required fields
        incomplete_item = {
            "product_id": 12345,
            # Missing 'quantity', 'product_description', 'price'
        }

        # Perform POST request with incomplete item data
        response = self.client.post(
            f"{BASE_URL}/{order1.id}/items",
            json=incomplete_item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_sad_path_order_not_found(self):
        """Test adding a new item to a non-existent order."""
        non_existent_order_id = 99999

        # Perform POST request to add item to a non-existent order
        response = self.client.post(
            f"{BASE_URL}/{non_existent_order_id}/items",
            json={
                "product_id": 12345,
                "quantity": 1,
                "product_description": "Test Product",
                "price": 10.99,
            },
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """Check if post request returns unsupported media type correctly"""
        response = self.client.post("/orders", data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_delete_root_not_allowed(self):
        """Check if root can be deleted"""
        response = self.client.delete("/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_items_in_order(self):
        """It should list all items in an order"""
        customer_id = random.randint(0, 10000)

        order = Order(
            customer_id=customer_id,
            shipping_address="726 Broadway, NY 10003",
            created_at=datetime.now(),
            status="CREATED",
        )
        order.create()

        item1 = Item(
            order_id=order.id,
            product_id=1,
            quantity=2,
            price=23.4,
            product_description="Apple",
        )
        item1.create()

        item2 = Item(
            order_id=order.id,
            product_id=2,
            quantity=5,
            price=50.0,
            product_description="Banana",
        )
        item2.create()

        response = self.client.get(
            f"/orders/{order.id}/items", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items_list = response.get_json()
        self.assertIsInstance(items_list, list)
        self.assertEqual(len(items_list), 2)

        self.assertEqual(items_list[0]["product_id"], item1.product_id)
        self.assertEqual(items_list[0]["quantity"], item1.quantity)
        self.assertEqual(items_list[0]["price"], item1.price)
        self.assertEqual(
            items_list[0]["product_description"], item1.product_description
        )

        self.assertEqual(items_list[1]["product_id"], item2.product_id)
        self.assertEqual(items_list[1]["quantity"], item2.quantity)
        self.assertEqual(items_list[1]["price"], item2.price)
        self.assertEqual(
            items_list[1]["product_description"], item2.product_description
        )

    def test_list_items_in_nonexistent_order(self):
        """It should check if the order does not exist"""
        non_existent_order_id = random.randint(10001, 20000)

        response = self.client.get(
            f"/orders/{non_existent_order_id}/items",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
