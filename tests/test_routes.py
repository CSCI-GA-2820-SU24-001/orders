"""
TestYourResourceModel API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, YourResourceModel
from requests import Request


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """ REST API Server Tests """

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
        db.session.query(YourResourceModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...

    def test_create(self):
        """ 
        It should call the method to create an order and return a 201 status code
        if created
        """
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()

        response = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order_data = response.get_json()

        # self.assertEqual(order_data["item_ids"], order.items, "Names does not match")
        self.assertEqual(
            order_data["customer_id"],
            order.customer_id,
            "customer id does not match",
        )
        self.assertEqual(order_data["items"], order.items, "Items does not match")
