"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    ProgrammingError,
    DataError,
    DatabaseError,
)
from wsgi import app
from service.models import (
    db,
    Order,
    Item,
    DataValidationError,
)
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# pylint: disable=duplicate-code
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
        """It should create an Order with an Item and add it to the database"""
        # Ensure the database is initially empty
        orders = Order.all()
        self.assertEqual(orders, [])

        # Create an Order and an Item
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()

        # Assert that the order was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 1)
        self.assertEqual(new_order.items[0].product_id, item.product_id)

        # Add another Item to the Order
        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].product_id, item2.product_id)

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

    @patch("service.models.db.session.commit")
    def test_add_order_failed(self, exception_mock):
        """It should not create an order if there is a database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.create)

    @patch("service.models.db.session.commit")
    def test_delete_order_failed(self, exception_mock):
        """It should delete an order if there is a database error"""
        order = OrderFactory()
        order.create()
        exception_mock.side_effect = Exception()
        self.assertRaises(DataValidationError, order.delete)

    @patch("service.models.db.session.commit")
    def test_update_order_failed(self, exception_mock):
        """It should not update an order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.update)

    @patch("service.models.db.session.commit")
    def test_create_item_failed(self, exception_mock):
        """It should not create an item if there is a database error"""
        exception_mock.side_effect = Exception()
        item = ItemFactory()
        self.assertRaises(DataValidationError, item.create)

    @patch("service.models.db.session.commit")
    def test_update_item_failed(self, exception_mock):
        """It should not update an item on database error"""
        exception_mock.side_effect = Exception()
        item = ItemFactory()
        self.assertRaises(DataValidationError, item.update)

    def test_deserialize_item(self):
        """
        Test if Item can be serialized with bad data types
        """
        with self.assertRaises(DataValidationError):
            item = ItemFactory()
            item.create()
            new_item = Item()
            dc = item.serialize()
            dc["quantity"] = "Hello"
            new_item.deserialize(dc)

        with self.assertRaises(DataValidationError):
            item = ItemFactory()
            item.create()
            new_item = Item()
            dc = item.serialize()
            dc["price"] = "Hello"
            new_item.deserialize(dc)

    def test_deserialize_order(self):
        """
        Test if order can be serialized with bad data types
        """
        # with self.assertRaises(DataValidationError):
        # order = OrderFactory()
        # order.create()
        # new_order = Order()
        # dc = order.serialize()
        # dc["created_at"] = "Hello"
        # new_order.deserialize(dc)

        with self.assertRaises(DataValidationError):
            order = OrderFactory()
            order.create()
            new_order = Order()
            dc = order.serialize()
            dc["status"] = "Hello"
            new_order.deserialize(dc)

    def test_show_all_items(self):
        """
        Test if all items can be viewed

        Returns:
            list of Item: A list of all Items in the database
        """
        try:
            items = Item.all()
            return items
        except (
            IntegrityError,
            OperationalError,
            ProgrammingError,
            DataError,
            DatabaseError,
        ) as e:
            return ("Unable to view all items. Error: ", e)

    def test_find_item(self):
        """Test if an item can be found in the database

        Args:
            item_id (int): ID of order to be searched
        """
        try:
            return Item.find(0)
        except (
            IntegrityError,
            OperationalError,
            ProgrammingError,
            DataError,
            DatabaseError,
        ) as e:
            return ("Unable to view all items. Error: ", e)

    def test_find_by_status(self):
        """It should Find Orders by Status"""
        for _ in range(10):
            OrderFactory().create()
        orders = Order.all()
        status_filter = orders[0].status
        status_count = len([order for order in orders if order.status == status_filter])
        found = Order.find_by_status(status_filter.name)
        self.assertEqual(found.count(), status_count)
        for order in found:
            self.assertEqual(order.status, status_filter)
