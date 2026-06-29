from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product
from orders.models import PickupLocation


class Command(BaseCommand):
    help = "Seed categories, products, and pickup locations for the Tefas Pharmacy demo."

    def handle(self, *args, **options):
        categories = {}
        for name in ["Painkillers", "Vitamins", "First Aid"]:
            category, _ = Category.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
            if not category.slug:
                category.slug = slugify(name)
                category.save(update_fields=["slug"])
            categories[name] = category

        product_data = [
            {
                "name": "Painkillers",
                "category": categories["Painkillers"],
                "price": "100.00",
                "short_description": "Relieves pain and fever",
                "description": "A reliable over-the-counter painkiller for fast relief from common pain and fever symptoms.",
            },
            {
                "name": "Vitamins",
                "category": categories["Vitamins"],
                "price": "100.00",
                "short_description": "Boosts body immunity",
                "description": "Daily vitamins to support general wellness and help maintain a healthy immune system.",
            },
            {
                "name": "First Aid Products",
                "category": categories["First Aid"],
                "price": "100.00",
                "short_description": "For wound care",
                "description": "Basic first aid essentials for dressing, cleansing, and protecting minor wounds.",
            },
        ]

        for item in product_data:
            defaults = {
                "slug": slugify(item["name"]),
                "price": item["price"],
                "short_description": item["short_description"],
                "description": item["description"],
                "stock_quantity": 25,
                "is_active": True,
            }
            product, created = Product.objects.get_or_create(name=item["name"], defaults={**defaults, "category": item["category"]})
            if not created:
                updated = False
                for field_name, value in {**defaults, "category": item["category"]}.items():
                    if getattr(product, field_name) != value:
                        setattr(product, field_name, value)
                        updated = True
                if updated:
                    product.save()

        pickup_locations = [
            ("Tefas Pharmacy CBD Branch", "Moi Avenue, Nairobi"),
            ("Tefas Pharmacy Westlands Branch", "Waiyaki Way, Nairobi"),
        ]
        for name, address in pickup_locations:
            PickupLocation.objects.get_or_create(name=name, address=address, defaults={"is_active": True})

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))