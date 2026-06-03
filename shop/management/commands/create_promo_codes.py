from django.core.management.base import BaseCommand
from shop.models import PromoCode


class Command(BaseCommand):
    help = 'Create default promo codes'

    def handle(self, *args, **options):
        promo_codes = [
            {'code': 'Vrund50', 'discount_percent': 50, 'is_active': True},
        ]

        for promo_data in promo_codes:
            promo_code, created = PromoCode.objects.get_or_create(
                code=promo_data['code'],
                defaults={
                    'discount_percent': promo_data['discount_percent'],
                    'is_active': promo_data['is_active'],
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created promo code: {promo_code.code} ({promo_code.discount_percent}%)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Promo code already exists: {promo_code.code}'
                    )
                )
