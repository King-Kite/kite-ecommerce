from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import (
                                    DetailView,
                                    ListView,
                                    TemplateView,
                                    View,
                                    DeleteView
                                    )
from users.forms import ContactUsForm
from .models import Category, Product, Review, Type
from .forms import ReviewForm


class AboutUsView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'Kite'
        return context


class CategoryView(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'pages/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'Kite'
        return context


class HomeView(TemplateView):
    model = Product
    template_name = 'pages/home.html'

    def queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        mattress = Category.objects.filter(name='mattress').first()

        context = super().get_context_data(**kwargs)
        context['form'] = ContactUsForm()
        context['featured_mattress'] = Product.objects.filter(category=mattress, featured=True).first()
        context['featured_others'] = Product.objects.exclude(category=mattress, featured=False)[:2]
        context['new_products'] = Product.objects.filter(new=True)[:3]
        context['site_name'] = 'Kite'
        return context


class ProductInfoView(View):
    def check_user_reviews(self, slug):
        obj_product = Product.objects.get(slug=slug)
        if self.request.user.is_authenticated:
            for product_review in self.request.user.reviews.all():
                if product_review.product == obj_product:
                    return product_review
        else:
            return HttpResponseForbidden()

    def get(self, request, slug):
        obj_product = Product.objects.get(slug=slug)
        related_products = Product.objects.filter(category=obj_product.category)[:4]
        reviews = obj_product.reviews.all().order_by('-update_date')
        paginator = Paginator(reviews, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'form': ReviewForm(),
            'obj_product': obj_product,
            'page_obj': page_obj,
            'product_review': self.check_user_reviews(obj_product.slug),
            'related_products': related_products,
            'site_name': 'Kite'
        }
        return render(request, 'pages/product-info.html', context)

    def post(self, request, slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        obj_product = Product.objects.get(slug=slug)
        form = ReviewForm(request.POST)
        if form.is_valid():
            author = request.user
            product = obj_product
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']

            user_product_review = self.check_user_reviews(obj_product.slug)
            if user_product_review is not None:
                messages.info(request, 'You already have a review for this product.')
            else:
                user_review = Review.objects.create(
                    author = author,
                    product = product,
                    body = body,
                    rating = rating
                    )
                user_review.save()
                messages.info(request, 'You Review was added.')
        return redirect('product-info', slug=obj_product.slug)


class ProductsView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_active=True)
    paginate_by = 15
    template_name = 'pages/products.html'

    def get_context_data(self, **kwargs):
        mattress = Category.objects.filter(name='mattress').first()
        pillow = Category.objects.filter(name='pillow').first()
        foam = Category.objects.filter(name='foam').first()

        context = super().get_context_data(**kwargs)
        context['mattresses'] = Product.objects.filter(category=mattress, is_active=True)[:3]
        context['pillows'] = Product.objects.filter(category=pillow)[:3]
        context['foams'] = Product.objects.filter(category=foam)[:3]
        context['site_name'] = 'Kite'
        return context


class ReviewUpdate(LoginRequiredMixin, View):
    form_class = ReviewForm
    template_name = 'pages/review-update.html'


    def get(self, request, *args, **kwargs):
        review = Review.objects.get(pk=kwargs['pk'])
        form = self.form_class(initial={'body': review.body, 'rating': review.rating})
        return render(request, self.template_name, {'form': form, 'review':review, 'site_name': 'Kite'})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        review = Review.objects.get(pk=kwargs['pk'])
        form = self.form_class(request.POST, initial={'body': review.body, 'rating': review.rating})
        if form.is_valid():
            review.body = form.cleaned_data.get('body')
            review.rating = form.cleaned_data.get('rating')
            review.save()

            messages.success(request, f'Your review update was successful!')
            return redirect('product-info', slug=review.product.slug)
        return render(request, self.template_name, {'form': form})


class ReviewDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'pages/review-delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'Kite'

    def get_success_url(self):
        review = self.get_object()
        return reverse('product-info', kwargs={'slug':review.product.slug})

    def test_func(self):
        review = self.get_object()
        if self.request.user == review.author:
            return True
        return False


class SearchResultsView(ListView):
    model = Product
    template_name = 'pages/search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if (query is not None) and (query != '') :
            product_list = Product.objects.filter(
                    Q(type__name__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(name__icontains=query)
                    , is_active=True
                )
            return product_list
        elif (query is None) or (query == ''):
            messages.info(self.request, 'Please provide a valid Input!')
            return redirect('search')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)[:12]
        context['site_name'] = 'Kite'
        return context
