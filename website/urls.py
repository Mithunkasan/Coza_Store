from django.urls import path
from .views import *
from website import views

urlpatterns = [

    # ---------------- HOME ----------------
    path('', index, name='home'),
    path('home2/', home2, name='home2'),
    path('home3/', home3, name='home3'),
    path('details/', productdetails, name='details'),

    # ---------------- AUTHENTICATION ----------------
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ---------------- PRODUCTS ----------------
    path('products/', product_list, name='product_list'),
    path('recommend/<int:product_id>/', recommend_products, name='recommend_products'),
    path('liked/', user_liked, name='user_liked'),

    # ---------------- CART SYSTEM 🛒 ----------------
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('remove-from-cart/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),

    # ---------------- PAGES ----------------
    path('about/', about, name='about'),
    path('tips/', tips, name='tips'),
    path('checkout/', checkout, name='checkout'),
    path('checkout-single/<int:cart_id>/', views.checkout_single, name='checkout_single'),
    path('place-order/', place_order, name='place_order'),

    # ---------------- SEARCH ----------------
    path('search/', search_products, name='search'),
    path('view-similar/<str:category>/', view_similar, name='view_similar'),

]