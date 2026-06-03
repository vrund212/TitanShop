import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TitanMarketplace.settings')
django.setup()

from shop.models import Product, Category

print('Products count:', Product.objects.filter(available=True).count())
print('Categories count:', Category.objects.count())
products = Product.objects.filter(available=True)[:3]
for p in products:
    print('Product:', p.name)
categories = Category.objects.all()[:3]
for c in categories:
    print('Category:', c.name)