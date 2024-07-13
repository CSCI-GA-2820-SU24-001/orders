"""
Test Factory to make fake objects for testing
"""

from datetime import datetime, timezone
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
from service.models import Order, Item, OrderStatus


class OrderFactory(Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Order

    id = Sequence(lambda n: n)
    customer_id = Faker("random_digit")
    shipping_address = Faker("street_address")
    created_at = FuzzyDateTime(datetime(2024, 1, 1, tzinfo=timezone.utc))
    status = FuzzyChoice(
        choices=[OrderStatus.COMPLETED, OrderStatus.CREATED, OrderStatus.PROCESSING]
    )

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = Sequence(lambda n: n)
    order_id = None
    product_id = Faker("random_digit")
    product_description = Faker("name")
    quantity = Faker("random_digit")
    price = Faker("pyfloat", min_value=0, max_value=1000)
    order = SubFactory(OrderFactory)
