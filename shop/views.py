from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Category, Product, OrderItem
from .forms import OrderCreateForm, CartAddProductForm
from .cart import Cart


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    min_p = request.GET.get("min_price")
    max_p = request.GET.get("max_price")

    if min_p:
        products = products.filter(price__gte=min_p)
    if max_p:
        products = products.filter(price__lte=max_p)

    sort = request.GET.get("sort")
    sort_mapping = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created",
        "oldest": "created",
    }

    if sort in sort_mapping:
        products = products.order_by(sort_mapping[sort])

    return render(
        request,
        "shop/product/list.html",
        {
            "category": category,
            "categories": categories,
            "products": products,
            "current_sort": sort,
        },
    )


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product, 
        id=id, 
        slug=slug, 
        available=True
        )
    cart_product_form = CartAddProductForm()
    return render(
        request,
        "shop/product/detail.html",
        {"product": product, "cart_product_form": cart_product_form},
    )


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
              quantity=cd["quantity"],
                override_quantity=cd["override"]
        )
    return redirect("shop:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("shop:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    return render(request, "shop/cart/detail.html", {"cart": cart})


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear()
            return render(
                request,
                  "shop/order/created.html",
                    {"order": order})
    else:
        form = OrderCreateForm()
    return render(
        request,
          "shop/order/create.html",
            {"cart": cart, "form": form}
            )
