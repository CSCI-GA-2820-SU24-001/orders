"""
Models for Orders

All of the models are stored in this module
"""

import logging
import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Item(db.Model):
    """
    Class that represents a Item in an Order
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.String(16), nullable=False)
    product_description = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Item id=[{self.id}]>"

    def create(self):
        """
        Creates a Item to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Item to the database
        """
        logger.info("Saving %s", self.id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Item from the data store"""
        logger.info("Deleting %s", self.id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Item into a dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "order_id": self.order_id,
            "product_description": self.product_description,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data):
        """
        Deserializes a Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.order_id = data["order_id"]
            self.product_description = data["product_description"]
            try:
                quantity = int(data["quantity"])
                self.quantity = quantity
            except Exception as e:
                raise DataValidationError(
                    "Invalid type for int [quantity]: " + data["quantity"]
                ) from e
            try:
                price = float(data["price"])
                self.price = price
            except Exception as e:
                raise DataValidationError(
                    "Invalid type for float [price]: " + data["price"]
                ) from e

        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Items in the database"""
        logger.info("Processing all Items")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Item by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)


class OrderStatus(Enum):
    """Enumeration of valid Order Status"""

    CREATED = 0
    PROCESSING = 1
    COMPLETED = 2


class Order(db.Model):
    """
    Class that represents an Order
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(16), nullable=False)
    shipping_address = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=False), nullable=False)
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.CREATED.name)
    )
    items = db.relationship("Item", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order id=[{self.id}]>"

    def create(self):
        """
        Creates a Order to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Order to the database
        """
        logger.info("Saving %s", self.id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Order from the data store"""
        logger.info("Deleting %s", self.id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Order into a dictionary"""
        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "shipping_address": self.shipping_address,
            "created_at": self.created_at,
            "status": self.status.name,
            "items": [],
        }
        for item in self.items:
            order["items"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Deserializes a Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.shipping_address = data["shipping_address"]

            if isinstance(data["created_at"], str):
                data["created_at"] = datetime.datetime.strptime(
                    data["created_at"], "%a, %d %b %Y %H:%M:%S %Z"
                )
            elif isinstance(data["created_at"], datetime.datetime):
                self.created_at = data["created_at"]
            else:
                raise DataValidationError(
                    "Invalid type for datetime [created_at]: "
                    + datetime.datetime.strftime(data["created_at"], DATE_FORMAT)
                )

            try:
                status = OrderStatus[data["status"].upper()]
                self.status = status
            except Exception as e:
                raise DataValidationError(
                    "Invalid type for Status [status]: " + data["status"]
                ) from e

            item_list = data.get("items")
            for item_data in item_list:
                item = Item()
                item.deserialize(item_data)
                self.items.append(item)

        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Orders in the database"""
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Order by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id: str) -> list:
        """Returns all Orders owned by a customer

        :param customer_id: the customer id to match against
        :type customer_id: str

        :return: a collection of Orders
        :rtype: list

        """
        logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_status(cls, status: str) -> list:
        """Returns all Orders owned by order status

        :param status: the status to match against
        :type status: str
        :return: a collection of Orders
        :rtype: list

        """
        logger.info("Processing status query for %s ...", status)
        status_enum = OrderStatus[status]
        return cls.query.filter(cls.status == status_enum)
