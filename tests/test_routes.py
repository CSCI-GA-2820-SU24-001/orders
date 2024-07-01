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
from service.models import db, Order

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
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...

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
