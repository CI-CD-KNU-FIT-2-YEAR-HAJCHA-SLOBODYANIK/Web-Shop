from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request, category_slug=None):

    category = None
    categories = Category.objects.all()
    
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    min_p = request.GET.get('min_price')
    max_p = request.GET.get('max_price')

    if min_p:
        products = products.filter(price__gte=min_p)

    if max_p:
        products = products.filter(price__lte=max_p)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):

    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    return render(request, 'shop/product/detail.html', {'product': product})

def order_create(request):
    cart = Cart(request) # Предполагается наличие класса Cart
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            cart.clear()
            return render(request, 'shop/order/created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'shop/order/create.html', {'cart': cart, 'form': form})