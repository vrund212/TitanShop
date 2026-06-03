import json
import urllib.request

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from shop.models import Category, Product, Review, SubCategory


def _titleize_category(raw_value):
    return str(raw_value or '').replace('-', ' ').replace('_', ' ').title().strip() or 'Products'


class Command(BaseCommand):
    help = 'Import products and reviews from the DummyJSON products API.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Number of products to import. 0 imports all available products.')
        parser.add_argument('--replace', action='store_true', help='Delete previously imported DummyJSON products before importing again.')

    def handle(self, *args, **options):
        limit = options['limit']
        endpoint = 'https://dummyjson.com/products?limit={}'.format(limit if limit > 0 else 0)

        try:
            request = urllib.request.Request(
                endpoint,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                }
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except Exception as exc:
            raise RuntimeError('Could not fetch DummyJSON products: {}'.format(exc))

        products = payload.get('products', [])
        if not products:
            self.stdout.write(self.style.WARNING('No products were returned from DummyJSON.'))
            return

        imported_count = 0
        review_count = 0

        with transaction.atomic():
            if options['replace']:
                Product.objects.filter(external_source='dummyjson').delete()

            for item in products:
                category_name = _titleize_category(item.get('category'))
                category_slug = slugify(category_name)[:200]
                category, _ = Category.objects.get_or_create(
                    slug=category_slug,
                    defaults={'name': category_name},
                )

                brand_name = (item.get('brand') or category_name).strip()[:200]
                brand_slug_base = slugify(brand_name)[:180] or category_slug
                subcategory_slug = '{}-{}'.format(brand_slug_base, category_slug)[:200]
                subcategory, _ = SubCategory.objects.get_or_create(
                    slug=subcategory_slug,
                    defaults={'name': brand_name, 'category': category},
                )
                if subcategory.category_id != category.id:
                    subcategory.category = category
                    subcategory.save(update_fields=['category'])

                title = (item.get('title') or 'DummyJSON Product').strip()[:200]
                slug = '{}-{}'.format(slugify(title)[:180], item.get('id'))[:200]
                thumbnail = item.get('thumbnail') or ''
                description_parts = [item.get('description', '').strip()]
                if item.get('brand'):
                    description_parts.append('Brand: {}'.format(item['brand']))
                if item.get('warrantyInformation'):
                    description_parts.append('Warranty: {}'.format(item['warrantyInformation']))
                if item.get('shippingInformation'):
                    description_parts.append('Shipping: {}'.format(item['shippingInformation']))
                if item.get('availabilityStatus'):
                    description_parts.append('Availability: {}'.format(item['availabilityStatus']))
                if item.get('tags'):
                    description_parts.append('Tags: {}'.format(', '.join(item['tags'])))
                description = '\n'.join(part for part in description_parts if part)

                product, created = Product.objects.update_or_create(
                    external_source='dummyjson',
                    external_source_id=item['id'],
                    defaults={
                        'category': category,
                        'subCategory': subcategory,
                        'name': title,
                        'slug': slug,
                        'external_image_url': thumbnail,
                        'description': description,
                        'price': int(round(float(item.get('price') or 0))),
                        'discount_price': float(item.get('price') or 0),
                        'stock': max(int(item.get('stock') or 0), 0),
                        'available': bool(item.get('stock', 0) or item.get('availabilityStatus') == 'In Stock'),
                    },
                )

                product_reviews = item.get('reviews') or []
                Review.objects.filter(product=product, user_name__startswith='dummyjson_').delete()
                for index, review_item in enumerate(product_reviews, start=1):
                    reviewer = review_item.get('reviewerName') or 'DummyJSON Reviewer {}'.format(index)
                    parsed_date = parse_datetime(review_item.get('date') or '')
                    if parsed_date is None:
                        parsed_date = timezone.now()
                    Review.objects.create(
                        product=product,
                        user_name='dummyjson_{}'.format(slugify(reviewer)[:80] or index),
                        rating=max(1, min(5, int(round(float(review_item.get('rating') or 0))))),
                        comment=(review_item.get('comment') or 'Imported from DummyJSON.')[:200],
                        pub_date=parsed_date,
                    )
                    review_count += 1

                imported_count += 1
                if created:
                    self.stdout.write('Imported {}'.format(product.name))
                else:
                    self.stdout.write('Updated {}'.format(product.name))

        self.stdout.write(self.style.SUCCESS(
            'DummyJSON import complete: {} products and {} reviews processed.'.format(imported_count, review_count)
        ))
