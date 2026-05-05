import pytest
from decimal import Decimal
from shop.cart import Cart


class MockProduct:
    def __init__(self, product_id, price):
        self.id = product_id
        self.price = price


class MockSession(dict):
    """
    Клас для імітації сесії Django, 
    який підтримує словникові методи та атрибут modified.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False


@pytest.fixture
def mock_request():
    """Фікстура для імітації запиту з сесією."""

    class Request:
        def __init__(self):
            self.session = MockSession()

    return Request()


def test_add_to_cart(mock_request):
    """Перевірка додавання товару до кошика."""
    cart = Cart(mock_request)
    product = MockProduct(
        product_id=1, 
        price=Decimal("15.50")
        )

    cart.add(product, quantity=2)

    product_key = str(product.id)
    assert product_key in cart.cart
    assert cart.cart[product_key]["quantity"] == 2
    assert cart.cart[product_key]["price"] == "15.50"


def test_add_existing_item(mock_request):
    """
    Перевірка додавання вже існуючого 
    товару (збільшення кількості).
    """
    cart = Cart(mock_request)
    product = MockProduct(product_id=1, price=Decimal("15.50"))

    cart.add(product, quantity=1)
    cart.add(product, quantity=2)

    product_key = str(product.id)
    assert cart.cart[product_key]["quantity"] == 3


def test_remove_item(mock_request):
    """Перевірка видалення товару з кошика."""
    cart = Cart(mock_request)
    product = MockProduct(product_id=1, price=Decimal("10.00"))

    cart.add(product, quantity=1)
    cart.remove(product)

    assert str(product.id) not in cart.cart


def test_get_total_price(mock_request):
    """Перевірка підрахунку загальної суми кошика."""
    cart = Cart(mock_request)
    product1 = MockProduct(product_id=1, price=Decimal("10.00"))
    product2 = MockProduct(product_id=2, price=Decimal("20.00"))

    cart.add(product1, quantity=2)
    cart.add(product2, quantity=1)

    total = cart.get_total_price()
    assert total == Decimal("40.00")


def test_clear_cart(mock_request):
    """Перевірка очищення кошика."""
    cart = Cart(mock_request)
    product = MockProduct(product_id=1, price=Decimal("10.00"))

    cart.add(product, quantity=1)
    cart.clear()

    with pytest.raises(KeyError):
        _ = mock_request.session["cart"]
