import pytest
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from shop.models import Category, Product


@pytest.mark.django_db
def test_product_list_view(client):
    """Перевірка відображення списку товарів та фільтрації."""
    category = Category.objects.create(name="Електроніка", slug="electronics")
    Product.objects.create(
        category=category,
        name="Ноутбук",
        slug="notebook",
        price=Decimal("1000.00"),
        available=True,
    )

    url = reverse("shop:product_list")
    response = client.get(url)

    assert response.status_code == 200
    assert "Ноутбук" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_product_detail_view(client):
    """Перевірка сторінки деталей конкретного товару."""
    category = Category.objects.create(name="Електроніка", slug="electronics")
    product = Product.objects.create(
        category=category,
        name="Ноутбук",
        slug="notebook",
        price=Decimal("1000.00"),
        available=True,
    )

    url = reverse("shop:product_detail", args=[product.id, product.slug])
    response = client.get(url)

    assert response.status_code == 200
    assert product.name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_cart_add_view(client):
    """Перевірка додавання товару в кошик через view (POST-запит)."""
    category = Category.objects.create(name="Електроніка", slug="electronics")
    product = Product.objects.create(
        category=category,
        name="Ноутбук",
        slug="notebook",
        price=Decimal("1000.00"),
        available=True,
    )

    url = reverse("shop:cart_add", args=[product.id])
    response = client.post(url, data={"quantity": 2, "override": False})

    assert response.status_code == 302
    session = client.session
    cart_data = session.get(settings.CART_SESSION_ID)

    assert cart_data is not None
    assert str(product.id) in cart_data
