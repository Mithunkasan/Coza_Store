from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Product, Cart

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os, random
import qrcode
import base64
from io import BytesIO


def generate_upi_qr(amount):
    upi_id = "yourupi@bank"   # 🔥 change this
    name = "Green Fashion"

    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"

    qr = qrcode.make(upi_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


# ---------------- HOME PAGES ----------------

def index(request):
    return render(request, 'index.html')

def home2(request):
    return render(request, 'home-02.html')

def home3(request):
    return render(request, 'home-03.html')

def productdetails(request):
    return render(request, 'product-detail.html')

def about(request):
    return render(request, 'about.html')

def tips(request):
    return render(request, 'tips.html')


# ---------------- AUTHENTICATION ----------------

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html",
                          {"error": "Username already exists"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('product_list')

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,
                            username=username,
                            password=password)

        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, "login.html",
                          {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------- PRODUCT LIST ----------------

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


# ---------------- RECOMMENDATION SYSTEM ----------------

def recommend_products(request, product_id):
    target = get_object_or_404(Product, id=product_id)

    if 'click_counts' not in request.session:
        request.session['click_counts'] = {}

    clicks = request.session['click_counts']
    clicks[str(product_id)] = clicks.get(str(product_id), 0) + 1
    request.session['click_counts'] = clicks

    products = Product.objects.all()
    df = pd.DataFrame(list(products.values(
        'id', 'name', 'category',
        'sustainability_score',
        'ethical_score'
    )))

    df_encoded = pd.get_dummies(df['category'])

    df_features = pd.concat([
        df[['sustainability_score', 'ethical_score']],
        df_encoded
    ], axis=1)

    similarity = cosine_similarity(df_features)

    target_index = df.index[df['id'] == product_id][0]

    similar_indices = similarity[target_index].argsort()[::-1][1:4]

    recommended_ids = df.iloc[similar_indices]['id'].values

    recommended_products = Product.objects.filter(id__in=recommended_ids)

    return render(request, 'recommendation.html', {
        'target': target,
        'recommended_products': recommended_products
    })


# ---------------- USER LIKED PRODUCTS ----------------

def user_liked(request):
    click_counts = request.session.get('click_counts', {})

    sorted_clicks = sorted(
        click_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    liked_products = []

    for prod_id, count in sorted_clicks:
        try:
            product = Product.objects.get(id=prod_id)
            product.click_count = count
            liked_products.append(product)
        except Product.DoesNotExist:
            continue

    return render(request, 'user_liked.html',
                  {'liked_products': liked_products})


# ---------------- CART SYSTEM ----------------

@login_required
def add_to_cart(request, product_id):

    # ✅ CASE 1: Product exists in DB
    if Product.objects.filter(id=product_id).exists():
        product = Product.objects.get(id=product_id)

    else:
        # ✅ CASE 2: Create product from search
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.POST.get("image")

        # 🔥 Create or get product (avoid duplicates)
        product, created = Product.objects.get_or_create(
            name=name,
            price=price,
            defaults={
                'category': 'search',
                'brand': 'Unknown',
                'condition': 'New',
                'sustainability_score': 80,
                'ethical_score': 80,
                'image_url': image
            }
        )

    # ✅ NOW always valid product → safe to add
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    item.delete()

    return redirect('view_cart')


# ---------------- CHECKOUT SYSTEM ----------------

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('view_cart')

    total = 0
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    # ✅ Generate dynamic QR
    qr_code = generate_upi_qr(total)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'qr_code': qr_code
    })
# ---------------- SEARCH SYSTEM ----------------

def search_products(request):
    query = request.GET.get('query', '').lower().strip()

    base_path = os.path.join(settings.MEDIA_ROOT, query)

    products = []

    if os.path.exists(base_path):
        all_images = os.listdir(base_path)

        selected_images = random.sample(
            all_images,
            min(20, len(all_images))
        )
        for i, img in enumerate(selected_images):
            products.append({
                'id': i + 1,  # ✅ ADD THIS LINE
                'image': f'{settings.MEDIA_URL}{query}/{img}',
                'price': random.randint(1000, 5000),
                'sustainability': random.randint(60, 100),
                'ethical': random.randint(60, 100),
                'category': query,
            })
    

    return render(request, 'search_results.html',
                  {'products': products, 'query': query})


def view_similar(request, category):
    base_path = os.path.join(settings.MEDIA_ROOT, category)

    products = []

    if os.path.exists(base_path):
        all_images = os.listdir(base_path)

        selected_images = random.sample(
            all_images,
            min(20, len(all_images))
        )

        for img in selected_images:
            products.append({
                'image': f'{settings.MEDIA_URL}{category}/{img}',
                'price': random.randint(1000, 5000),
                'sustainability': random.randint(60, 100),
                'ethical': random.randint(60, 100),
                'category': category,
            })

    return render(request, 'search_results.html',
                  {'products': products, 'query': category})
@login_required
def place_order(request):

    if request.method == "POST":

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('view_cart')

        total = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

        # Clear cart after order
        cart_items.delete()

        return render(request, 'place_order.html', {
            'total': total
        })

    return redirect('checkout')

@login_required
def checkout_single(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    item.subtotal = item.product.price * item.quantity
    total = item.subtotal

    return render(request, 'checkout.html', {
        'cart_items': [item],   # 🔥 Only one item
        'total': total
    })