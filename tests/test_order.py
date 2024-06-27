"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from .factories import OrderFactory, ItemFactory

from service.models import db, Order, Item

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


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
        db.session.query(Item).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].id, item.id)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].id, item2.id)

    def test_update_order_item(self):
        """It should Update an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        old_item = order.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.price, item.price)
        # Change the price
        old_item.price = 3.0
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        item = order.items[0]
        self.assertEqual(item.price, 3.0)

    def test_delete_order_item(self):
        """It should Delete an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["order_id"], item.order_id)
        self.assertEqual(serial_item["product_id"], item.product_id)
        self.assertEqual(serial_item["product_description"], item.product_description)
        self.assertEqual(serial_item["price"], item.price)
        self.assertEqual(serial_item["quantity"], item.quantity)

    def test_deserialize_an_item(self):
        """It should deserialize an Item"""
        item = ItemFactory()
        item.create()
        new_item = Item()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.order_id, item.order_id)
        self.assertEqual(new_item.order_id, item.order_id)
        self.assertEqual(new_item.product_id, item.product_id)
        self.assertEqual(new_item.product_description, item.product_description)
        self.assertEqual(new_item.price, item.price)
        self.assertEqual(new_item.quantity, item.quantity)
