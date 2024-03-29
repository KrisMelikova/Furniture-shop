import datetime, random, os, json
from django.shortcuts import render, get_object_or_404
from mainapp.models import ProductCategory, Product
from basketapp.models import Basket
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

JSON_PATH = 'mainapp/json'


def load_from_json(file_name):
    with open(os.path.join(JSON_PATH, file_name + '.json'), 'r') as infile:
        return json.load(infile)


def get_hot_product():
    products = Product.objects.filter(is_active=True, category__is_active=True)

    return random.sample(list(products), 1)[0]


def get_same_products(hot_product):
    same_products = Product.objects.filter(category=hot_product.category, is_active=True).exclude(pk=hot_product.pk)[:3]

    return same_products


def main(request):
    title = 'главная'
    # products = Product.objects.filter(is_active=True, category__is_active=True)[:3]
    products = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')[:3]

    content = {
        'title': title,
        'products': products,
    }

    return render(request, 'mainapp/index.html', content)


@cache_page(3600)
def products(request, pk=None, page=1):
    title = 'продукты'
    # links_menu = ProductCategory.objects.filter(is_active=True)

    if pk:
        if pk == '0':
            category = {
                'pk': 0,
                'name': 'все'
            }
            products = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
        else:
            category = get_object_or_404(ProductCategory, pk=pk)
            products = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by(
                'price')

        paginator = Paginator(products, 2)
        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(paginator.num_pages)

        content = {
            'title': title,
            'links_menu': get_links_menu(),
            'category': category,
            'products': products_paginator,
        }

        return render(request, 'mainapp/products_list.html', content)

    hot_product = get_hot_product()
    same_products = get_same_products(hot_product)

    content = {
        'title': title,
        'links_menu': get_links_menu(),
        'hot_product': hot_product,
        'same_products': same_products,
    }

    return render(request, 'mainapp/products.html', content)


def product(request, pk):
    title = 'продукты'
    links_menu = ProductCategory.objects.filter(is_active=True)

    product = get_object_or_404(Product, pk=pk)
    # product = get_product(pk)

    content = {
        'title': title,
        'links_menu': get_links_menu(),
        'product': product,
    }
    return render(request, 'mainapp/product.html', content)


def contact(request):
    title = 'о нас'

    locations = load_from_json('contact__locations')

    content = {
        'title': title,
        'locations': locations,
    }

    return render(request, 'mainapp/contact.html', content)


def get_links_menu():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_product(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product_item = cache.get(key)
        if product_item is None:
            product_item = Product.objects.get(pk=pk)
            cache.set(key, product)
        return product_item
    else:
        return Product.objects.get(pk=pk)
