from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from .models import Product, Category, Order, OrderItem


class ShopComplexTest(TestCase):
    def setUp(self):
        self.cat_weapon = Category.objects.create(
            name="Заборонена зброя", slug="zaboronena-zbroya"
        )
        self.cat_people = Category.objects.create(name="Люди", slug="lyudi")
        self.cat_tanks = Category.objects.create(
            name="Радянська військова техніка", slug="tanks"
        )

        self.p1 = Product.objects.create(
            category=self.cat_weapon,
            name="РДС-1",
            slug="rds-1",
            price=Decimal("230.00"),
            available=True,
        )
        self.p2 = Product.objects.create(
            category=self.cat_weapon,
            name="Mark 15",
            slug="mark-15",
            price=Decimal("499.00"),
            available=True,
        )
        self.p3 = Product.objects.create(
            category=self.cat_people,
            name="Іван",
            slug="ivan",
            price=Decimal("15.00"),
            available=False,
        )
        self.p4 = Product.objects.create(
            category=self.cat_people,
            name="Петя",
            slug="petya",
            price=Decimal("20.00"),
            available=True,
        )
        self.p5 = Product.objects.create(
            category=self.cat_tanks,
            name="Т-80",
            slug="t-80",
            price=Decimal("3200.00"),
            available=True,
        )
        self.p6 = Product.objects.create(
            category=self.cat_tanks,
            name="Т-72",
            slug="t-72",
            price=Decimal("2600.00"),
            available=True,
        )
        self.p7 = Product.objects.create(
            category=self.cat_tanks,
            name="Т-55",
            slug="t-55",
            price=Decimal("1200.00"),
            available=True,
        )

    def test_availability_logic(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "РДС-1")
        self.assertNotContains(response, "Іван")

    def test_category_filtering(self):
        url = reverse("shop:product_list_by_category", args=[self.cat_people.slug])
        response = self.client.get(url)
        self.assertContains(response, "Петя")
        self.assertNotContains(response, "Т-80")

    def test_price_range_filter(self):
        response = self.client.get(
            reverse("shop:product_list"), {"min_price": "200", "max_price": "1000"}
        )
        self.assertContains(response, "РДС-1")
        self.assertContains(response, "Mark 15")
        self.assertNotContains(response, "Т-80")
        self.assertNotContains(response, "Петя")

    def test_sorting_logic(self):
        response = self.client.get(reverse("shop:product_list"), {"sort": "price_asc"})
        products = list(response.context["products"])
        self.assertEqual(products[0].name, "Петя")
        self.assertEqual(products[-1].name, "Т-80")

    def test_order_creation_integrity(self):
        order = Order.objects.create(
            first_name="Тест",
            last_name="Юзер",
            email="test@test.com",
            address="Місто",
            city="Місто",
        )
        OrderItem.objects.create(
            order=order, product=self.p5, price=self.p5.price, quantity=1
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().price, Decimal("3200.00"))

    def test_product_detail_view(self):
        url = reverse("shop:product_detail", args=[self.p1.id, self.p1.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "РДС-1")

    def test_order_total_and_items_retrieval(self):
        order = Order.objects.create(
            first_name="Тест",
            last_name="Юзер",
            email="test@test.com",
            address="Місто",
            city="Місто",
        )
        OrderItem.objects.create(
            order=order, product=self.p1, price=self.p1.price, quantity=2
        )
        OrderItem.objects.create(
            order=order, product=self.p2, price=self.p2.price, quantity=1
        )
        OrderItem.objects.create(
            order=order, product=self.p7, price=self.p7.price, quantity=3
        )

        expected_total = (self.p1.price * 2) + (self.p2.price * 1) + (self.p7.price * 3)
        self.assertEqual(order.get_total_cost(), expected_total)

        retrieved_products = [item.product for item in order.items.all()]
        self.assertIn(self.p1, retrieved_products)
        self.assertIn(self.p2, retrieved_products)
        self.assertIn(self.p7, retrieved_products)

    def test_price_integrity_after_order(self):
        order = Order.objects.create(
            first_name="Тест",
            last_name="Юзер",
            email="test@test.com",
            address="Місто",
            city="Місто",
        )
        original_price = self.p5.price
        item = OrderItem.objects.create(
            order=order, product=self.p5, price=original_price, quantity=1
        )

        self.p5.price += Decimal("1000.00")
        self.p5.save()

        order_item = OrderItem.objects.get(id=item.id)
        self.assertEqual(order_item.price, original_price)
        self.assertEqual(order.get_total_cost(), original_price)

        self.p5.price = original_price
        self.p5.save()
