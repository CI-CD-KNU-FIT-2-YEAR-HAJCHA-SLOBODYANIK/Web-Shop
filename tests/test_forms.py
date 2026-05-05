from shop.forms import OrderCreateForm, CartAddProductForm


def test_order_create_form_valid():
    """Перевірка валідності форми замовлення при введенні коректних даних."""
    form = OrderCreateForm(
        data={
            "first_name": "Іван",
            "last_name": "Іваненко",
            "email": "test@example.com",
            "address": "вул. Тестова, 1",
            "city": "Київ",
        }
    )
    assert form.is_valid()


def test_order_create_form_invalid():
    """
    Перевірка недійсності форми, 
    якщо не заповнено обов'язкові поля.
    """
    form = OrderCreateForm(data={})
    assert not form.is_valid()


def test_cart_add_product_form_valid():
    """
    Перевірка валідності форми додавання до кошика.
    """
    form = CartAddProductForm(
        data={"quantity": 2, 
              "override": False
              })
    assert form.is_valid()


def test_cart_add_product_form_out_of_range():
    """
    Перевірка помилки, 
    якщо кількість перевищує 
    допустимі значення (1-10).
    """
    form = CartAddProductForm(
        data={"quantity": 15, 
              "override": False}
              )
    assert not form.is_valid()
