import csv
from django.core.management.base import BaseCommand
from website.models import Product  # change 'App' to your app name if different

class Command(BaseCommand):
    help = 'Load products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        if not path:
            self.stdout.write(self.style.ERROR('Please provide a CSV path using --path'))
            return

        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Product.objects.create(
                    name=row['name'],
                    category=row['category'],
                    brand=row['brand'],
                    price=float(row['price']) if row['price'].strip() else 0.0,

                    condition=row['condition'],
                    sustainability_score=float(row['sustainability_score']) if row['sustainability_score'].strip() else 0.0,
                    ethical_score=float(row['ethical_score']) if row['ethical_score'].strip() else 0.0,

                    image_url=row['image_url']
                )
        self.stdout.write(self.style.SUCCESS('✅ Products loaded successfully!'))
