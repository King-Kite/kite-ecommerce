from django.urls import path, include
from products.views import AboutUsView, CategoryView, HomeView, ProductsView, ProductInfoView, ReviewUpdate, ReviewDelete, SearchResultsView
from users.views import ContactUsView, ProfileView, ProfileUpdateView
from orders.views import AddToCartView, CartView, CheckoutView, OrderSummaryView, RemoveSingleProductFromCartView, RemoveFromCartView
from wishlists.views import AddToWishlistView, RemoveFromWishlistView, WishlistView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutUsView.as_view(), name='about'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<int:pk>/add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('product/<int:pk>/add-to-wishlist/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('product/<int:pk>/remove-from-cart/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('product/<int:pk>/remove-from-wishlist/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    path('product/<int:pk>/remove-single-product-from-cart/', RemoveSingleProductFromCartView.as_view(), name='remove-single-product-from-cart'),
    path('product-info/<slug>/', ProductInfoView.as_view(), name='product-info'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/category/<slug>/', CategoryView.as_view(), name='category'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('review/<int:pk>/update/', ReviewUpdate.as_view(), name='review-update'),
    path('review/<int:pk>/delete/', ReviewDelete.as_view(), name='review-delete'),
    path('search/', csrf_exempt(SearchResultsView.as_view()), name='search'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
]

