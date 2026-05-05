import pytest
from decimal import Decimal
from shop.models import Category, Product, Order, OrderItem


@pytest.mark.django_db
def test_category_creation():
    """Перевірка створення категорії."""
    category = Category.objects.create(name="Електроніка", slug="electronics")

    assert category.name == "Електроніка"
    assert str(category) == "Електроніка"


@pytest.mark.django_db
def test_product_creation():
    """Перевірка створення товару та його зв'язку з категорією."""
    category = Category.objects.create(name="Електроніка", slug="electronics")

    product = Product.objects.create(
        category=category,
        name="Ноутбук",
        slug="notebook",
        price=Decimal("999.99"),
        available=True,
    )

    assert product.name == "Ноутбук"
    assert product.category == category
    assert str(product) == "Ноутбук"


@pytest.mark.django_db
def test_order_creation():
    """Перевірка створення замовлення та початкового статусу."""
    order = Order.objects.create(
        first_name="Іван",
        last_name="Іваненко",
        email="test@example.com",
        address="вул. Тестова, 1",
        city="Київ",
    )

    assert order.first_name == "Іван"
    assert str(order) == f"Замовлення {order.id}"
    assert order.paid is False
    assert order.get_total_cost() == Decimal("0")
