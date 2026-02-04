"""
Management command to test Apriori recommendations
Usage: python manage.py test_apriori
"""

from django.core.management.base import BaseCommand
from main.utils import run_apriori_analysis, get_product_recommendations
from main.models import Product, Order


class Command(BaseCommand):
    help = 'Test Apriori algorithm and show recommendations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Testing Apriori Recommendation System'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Check orders
        order_count = Order.objects.filter(
            status__in=['delivered', 'confirmed', 'processing', 'shipped']
        ).count()

        self.stdout.write(f'\nTotal orders for analysis: {order_count}')

        if order_count == 0:
            self.stdout.write(self.style.WARNING('\nNo orders found for Apriori analysis!'))
            self.stdout.write(self.style.WARNING('System will fall back to category-based recommendations.'))
            return

        # Run Apriori analysis
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('Running Apriori Analysis...')
        self.stdout.write('-' * 70)

        rules = run_apriori_analysis()

        if rules is None or rules.empty:
            self.stdout.write(self.style.WARNING('\nInsufficient data for Apriori rules.'))
            self.stdout.write(self.style.WARNING('Need at least 2 orders with multiple items each.'))
            self.stdout.write(self.style.WARNING('System will use fallback recommendations.'))
            return

        self.stdout.write(self.style.SUCCESS(f'\nGenerated {len(rules)} association rules!'))

        # Show top 10 rules
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('Top 10 Association Rules:')
        self.stdout.write('-' * 70)

        for idx, rule in rules.head(10).iterrows():
            antecedents_ids = list(rule['antecedents'])
            consequents_ids = list(rule['consequents'])

            # Get product names
            antecedent_products = Product.objects.filter(id__in=antecedents_ids)
            consequent_products = Product.objects.filter(id__in=consequents_ids)

            antecedent_names = [p.name for p in antecedent_products]
            consequent_names = [p.name for p in consequent_products]

            self.stdout.write(f'\nRule {idx + 1}:')
            self.stdout.write(f'  If customer buys: {", ".join(antecedent_names)}')
            self.stdout.write(f'  Then also buys: {", ".join(consequent_names)}')
            self.stdout.write(f'  Confidence: {rule["confidence"]:.2%}')
            self.stdout.write(f'  Support: {rule["support"]:.2%}')
            self.stdout.write(f'  Lift: {rule["lift"]:.2f}')

        # Test recommendations for active products
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('Testing Product Recommendations:')
        self.stdout.write('-' * 70)

        test_products = Product.objects.filter(is_active=True)[:5]

        for product in test_products:
            recommendations = get_product_recommendations(product.id, limit=4)

            self.stdout.write(f'\n{product.name} ({product.category.name if product.category else "No Category"}):')

            if recommendations:
                self.stdout.write(self.style.SUCCESS(f'  Found {len(recommendations)} Apriori-based recommendations:'))
                for rec in recommendations:
                    self.stdout.write(f'    - {rec.name} (₹{rec.price})')
            else:
                self.stdout.write(self.style.WARNING('  No Apriori recommendations (will use fallback)'))

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Apriori Test Complete!'))
        self.stdout.write('=' * 70)
