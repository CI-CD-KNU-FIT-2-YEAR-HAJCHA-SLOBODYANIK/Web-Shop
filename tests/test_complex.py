import pytest
from decimal import Decimal
from django.urls import reverse
from shop.models import Product, Category, Order, OrderItem


@pytest.fixture
def setup_shop_data(db):
    """
    Фікстура для створення
    початкових даних у базі.
    """
    cat_weapon = Category.objects.create(
        name="Заборонена зброя", slug="zaboronena-zbroya"
    )
    cat_people = Category.objects.create(name="Люди", slug="lyudi")
    cat_tanks = Category.objects.create(
        name="Радянська військова техніка", slug="tanks"
    )

    p1 = Product.objects.create(
        category=cat_weapon,
        name="РДС-1",
        slug="rds-1",
        price=Decimal("230.00"),
        available=True,
    )
    p2 = Product.objects.create(
        category=cat_weapon,
        name="Mark 15",
        slug="mark-15",
        price=Decimal("499.00"),
        available=True,
    )
    p3 = Product.objects.create(
        category=cat_people,
        name="Іван",
        slug="ivan",
        price=Decimal("15.00"),
        available=False,
    )
    p4 = Product.objects.create(
        category=cat_people,
        name="Петя",
        slug="petya",
        price=Decimal("20.00"),
        available=True,
    )
    p5 = Product.objects.create(
        category=cat_tanks,
        name="Т-80",
        slug="t-80",
        price=Decimal("3200.00"),
        available=True,
    )
    p6 = Product.objects.create(
        category=cat_tanks,
        name="Т-72",
        slug="t-72",
        price=Decimal("2600.00"),
        available=True,
    )
    p7 = Product.objects.create(
        category=cat_tanks,
        name="Т-55",
        slug="t-55",
        price=Decimal("1200.00"),
        available=True,
    )

    return {
        "cat_weapon": cat_weapon,
        "cat_people": cat_people,
        "cat_tanks": cat_tanks,
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4": p4,
        "p5": p5,
        "p6": p6,
        "p7": p7,
    }


def test_availability_logic(client, setup_shop_data):
    """
    Перевірка логіки відображення
      тільки доступних товарів.
    """
    response = client.get(reverse("shop:product_list"))
    assert response.status_code == 200
    assert "РДС-1" in response.content.decode("utf-8")
    assert "Іван" not in response.content.decode("utf-8")


def test_category_filtering(client, setup_shop_data):
    """Перевірка фільтрації за категорією."""
    url = reverse(
        "shop:product_list_by_category",
        args=[setup_shop_data["cat_people"].slug]
    )
    response = client.get(url)
    assert "Петя" in response.content.decode("utf-8")
    assert "Т-80" not in response.content.decode("utf-8")


def test_price_range_filter(client, setup_shop_data):
    """
    Перевірка фільтрації товарів
    за ціною (через GET-параметри).
    """
    response = client.get(
        reverse("shop:product_list"),
        {"min_price": "200", "max_price": "1000"}
    )

    content = response.content.decode("utf-8")
    assert "РДС-1" in content
    assert "Mark 15" in content
    assert "Т-80" not in content
    assert "Петя" not in content


def test_sorting_logic(client, setup_shop_data):
    """Перевірка сортування товарів за ціною."""
    response = client.get(
        reverse("shop:product_list"),
        {"sort": "price_asc"}
    )
    products = list(response.context["products"])
    assert products[0].name == "Петя"
    assert products[-1].name == "Т-80"


def test_price_integrity_after_order(setup_shop_data):
    """
    Перевірка збереження фіксованої
    ціни після зміни ціни в самому каталозі.
    """
    order = Order.objects.create(
        first_name="Тест",
        last_name="Юзер",
        email="test@test.com",
        address="Місто",
        city="Місто",
    )
    product = setup_shop_data["p5"]
    original_price = product.price

    item = OrderItem.objects.create(
        order=order,
        product=product,
        price=original_price,
        quantity=1
    )

    # Змінюємо ціну товару в каталозі
    product.price += Decimal("1000.00")
    product.save()

    order_item = OrderItem.objects.get(id=item.id)

    # Переконуємося, що в самому замовленні ціна залишилася незмінною
    assert order_item.price == original_price
    assert order.get_total_cost() == original_price