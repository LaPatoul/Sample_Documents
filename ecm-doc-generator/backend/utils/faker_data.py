from faker import Faker
import random
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, locale='fr_FR'):
        self.faker = Faker(locale)
        self.locale = locale

    def generate_company(self):
        """Generate a fake company"""
        country_map = {
            'en_GB': 'United Kingdom',
            'en_US': 'United States',
            'fr_FR': 'France',
            'de_DE': 'Germany',
            'es_ES': 'Spain',
        }
        return {
            'name': self.faker.company(),
            'address': self.faker.street_address(),
            'city': self.faker.city(),
            'postal_code': self.faker.postcode(),
            'country': country_map.get(self.locale, 'United Kingdom'),
            'phone': self.faker.phone_number(),
            'email': self.faker.company_email(),
            'tax_id': self.faker.bothify(text='??-########'),
            'website': self.faker.domain_name()
        }

    def generate_person(self):
        """Generate a fake person"""
        return {
            'name': self.faker.name(),
            'email': self.faker.email(),
            'phone': self.faker.phone_number(),
            'address': self.faker.address()
        }

    def generate_invoice_items(self, count=None):
        """Generate invoice line items"""
        if count is None:
            count = random.randint(5, 10)

        items = []
        services = [
            ('Consulting Services', 'hr', 80, 150),
            ('Software Development', 'hr', 100, 200),
            ('Project Management', 'hr', 90, 180),
            ('Technical Support', 'hr', 60, 120),
            ('System Integration', 'hr', 110, 190),
            ('Quality Assurance', 'hr', 70, 140),
            ('Database Management', 'hr', 85, 160),
            ('Network Configuration', 'hr', 95, 175),
            ('Security Audit', 'hr', 120, 220),
            ('Training Services', 'hr', 75, 145),
        ]

        for _ in range(count):
            service, unit, min_price, max_price = random.choice(services)
            quantity = random.randint(1, 40)
            unit_price = round(random.uniform(min_price, max_price), 2)
            total = round(quantity * unit_price, 2)

            items.append({
                'description': service,
                'quantity': quantity,
                'unit': unit,
                'unit_price': unit_price,
                'total': total
            })

        return items

    def generate_purchase_order_items(self, count=None):
        """Generate purchase order line items"""
        if count is None:
            count = random.randint(5, 10)

        items = []
        products = [
            ('Laptop Computer', 'pcs', 800, 1500),
            ('Office Desk', 'pcs', 200, 500),
            ('Office Chair', 'pcs', 150, 400),
            ('Monitor 27"', 'pcs', 250, 600),
            ('Printer Multifunction', 'pcs', 300, 800),
            ('Office Supplies Kit', 'kit', 50, 150),
            ('Network Switch', 'pcs', 400, 900),
            ('Server Rack', 'pcs', 500, 1200),
            ('Cables & Adapters', 'set', 30, 100),
            ('Software License', 'lic', 100, 500),
        ]

        for _ in range(count):
            product, unit, min_price, max_price = random.choice(products)
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(min_price, max_price), 2)
            total = round(quantity * unit_price, 2)

            items.append({
                'description': product,
                'quantity': quantity,
                'unit': unit,
                'unit_price': unit_price,
                'total': total
            })

        return items

    def generate_receipt_items(self, count=None):
        """Generate receipt line items"""
        if count is None:
            count = random.randint(2, 5)

        items = []
        products = [
            ('Coffee', 3.50, 5.50),
            ('Sandwich', 6.00, 9.00),
            ('Lunch Meal', 12.00, 18.00),
            ('Parking Fee', 5.00, 15.00),
            ('Office Supplies', 10.00, 30.00),
            ('Book', 15.00, 35.00),
            ('Taxi Fare', 20.00, 50.00),
        ]

        for _ in range(count):
            product, min_price, max_price = random.choice(products)
            quantity = random.randint(1, 3)
            unit_price = round(random.uniform(min_price, max_price), 2)
            total = round(quantity * unit_price, 2)

            items.append({
                'description': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total': total
            })

        return items

    def generate_date_range(self, start_date, end_date):
        """Generate a random date within a range"""
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)

    def generate_document_number(self, doc_type, year=None):
        """Generate a document number"""
        if year is None:
            year = datetime.now().year

        prefix_map = {
            'invoice': 'INV',
            'purchase_order': 'PO',
            'receipt': 'RCP'
        }

        prefix = prefix_map.get(doc_type, 'DOC')
        number = random.randint(1000, 9999)
        return f"{prefix}-{year}-{number}"

def get_generator(language='en-GB'):
    """Factory function to get appropriate data generator"""
    locale_map = {
        'en-GB': 'en_GB',
        'en-US': 'en_US',
        'fr': 'fr_FR',
        'de': 'de_DE',
        'es': 'es_ES',
    }
    return DataGenerator(locale_map.get(language, 'en_GB'))
