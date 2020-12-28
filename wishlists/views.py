from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, RedirectView
from products.models import Product, ProductVariant
from .models import Wishlist

class AddToWishlistView(LoginRequiredMixin, RedirectView):
    url = '/wishlist/'

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(ProductVariant, pk=kwargs['pk'])
        wishlist_queryset = Wishlist.objects.filter(user=self.request.user, product=product)
        if wishlist_queryset.exists():
            messages.info(self.request, 'This product is already on your wishlist')
        else:
            wishlist = Wishlist.objects.create(
                user = self.request.user,
                product = product
                )
            wishlist.save()
            messages.info(self.request, 'This product is already on your wishlist')
        return super().get_redirect_url(*args, **kwargs)

class RemoveFromWishlistView(LoginRequiredMixin, RedirectView):
    url = '/wishlist/'

    def get_redirect_url(self, *args, **kwargs):
        product = get_object_or_404(ProductVariant, pk=kwargs['pk'])
        wishlist_queryset = Wishlist.objects.filter(user=self.request.user, product=product)
        if wishlist_queryset.exists():
            wishlist = wishlist_queryset.first()
            wishlist.delete()
            messages.info(self.request, 'This product was removed from your wishlist')
        else:
            messages.info(self.request, 'This product is not on your wishlist')
        return super().get_redirect_url(*args, **kwargs)

class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    context_object_name = 'wishlist'
    paginate_by = 20
    template_name = 'pages/wishlist.html'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)[:4]
        return context
