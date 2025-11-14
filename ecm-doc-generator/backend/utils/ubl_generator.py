"""
UBL 2.1 XML Generator
Generates Universal Business Language compliant XML documents
"""
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class UBLGenerator:
    """Base class for UBL document generation"""

    # UBL 2.1 namespaces
    NAMESPACES = {
        'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    }

    def __init__(self):
        pass

    def _format_date(self, date_obj):
        """Format date to UBL standard (YYYY-MM-DD)"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime('%Y-%m-%d')

    def _format_amount(self, amount, currency='EUR'):
        """Format amount with currency"""
        return {
            'value': f"{amount:.2f}",
            'currencyID': currency
        }

    def _add_party(self, parent, party_data, party_type='AccountingSupplierParty'):
        """Add party information (supplier or customer)"""
        party_elem = SubElement(parent, f'cac:{party_type}')
        party = SubElement(party_elem, 'cac:Party')

        # Party Name
        party_name = SubElement(party, 'cac:PartyName')
        name = SubElement(party_name, 'cbc:Name')
        name.text = party_data.get('name', '')

        # Postal Address
        address = SubElement(party, 'cac:PostalAddress')
        street = SubElement(address, 'cbc:StreetName')
        street.text = party_data.get('address', '')
        city = SubElement(address, 'cbc:CityName')
        city.text = party_data.get('city', '')
        postal_code = SubElement(address, 'cbc:PostalZone')
        postal_code.text = party_data.get('postal_code', '')
        country = SubElement(address, 'cac:Country')
        country_code = SubElement(country, 'cbc:IdentificationCode')
        country_code.text = self._get_country_code(party_data.get('country', ''))

        # Contact
        if party_data.get('email') or party_data.get('phone'):
            contact = SubElement(party, 'cac:Contact')
            if party_data.get('phone'):
                telephone = SubElement(contact, 'cbc:Telephone')
                telephone.text = party_data.get('phone', '')
            if party_data.get('email'):
                email = SubElement(contact, 'cbc:ElectronicMail')
                email.text = party_data.get('email', '')

        return party_elem

    def _get_country_code(self, country_name):
        """Convert country name to ISO 3166-1 alpha-2 code"""
        country_map = {
            'United Kingdom': 'GB',
            'United States': 'US',
            'France': 'FR',
            'Germany': 'DE',
            'Spain': 'ES',
        }
        return country_map.get(country_name, 'GB')

    def _get_currency_code(self, language):
        """Get currency code based on language"""
        currency_map = {
            'en-GB': 'GBP',
            'en-US': 'USD',
            'fr': 'EUR',
            'de': 'EUR',
            'es': 'EUR',
            'it': 'EUR',
        }
        return currency_map.get(language, 'EUR')

    def _prettify_xml(self, elem):
        """Return a pretty-printed XML string"""
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


class InvoiceUBLGenerator(UBLGenerator):
    """Generate UBL 2.1 Invoice XML"""

    def generate(self, data, language='en-GB'):
        """Generate UBL Invoice XML

        Args:
            data: Dictionary with invoice data (company, customer, items, etc.)
            language: Language code for currency

        Returns:
            XML string
        """
        currency = self._get_currency_code(language)

        # Create root element
        root = Element('Invoice')
        for key, value in self.NAMESPACES.items():
            root.set(key, value)

        # UBL Version
        ubl_version = SubElement(root, 'cbc:UBLVersionID')
        ubl_version.text = '2.1'

        # Invoice ID
        invoice_id = SubElement(root, 'cbc:ID')
        invoice_id.text = data.get('invoice_number', 'INV-0001')

        # Issue Date
        issue_date = SubElement(root, 'cbc:IssueDate')
        issue_date.text = self._format_date(data.get('issue_date', datetime.now()))

        # Due Date
        if data.get('due_date'):
            due_date = SubElement(root, 'cbc:DueDate')
            due_date.text = self._format_date(data['due_date'])

        # Invoice Type Code (380 = Commercial invoice)
        invoice_type = SubElement(root, 'cbc:InvoiceTypeCode')
        invoice_type.text = '380'

        # Document Currency Code
        currency_code = SubElement(root, 'cbc:DocumentCurrencyCode')
        currency_code.text = currency

        # Order Reference (if linked)
        if data.get('order_number'):
            order_ref = SubElement(root, 'cac:OrderReference')
            order_id = SubElement(order_ref, 'cbc:ID')
            order_id.text = data['order_number']

        # Accounting Supplier Party (Company)
        self._add_party(root, data.get('company', {}), 'AccountingSupplierParty')

        # Accounting Customer Party
        self._add_party(root, data.get('customer', {}), 'AccountingCustomerParty')

        # Tax Total
        tax_total = SubElement(root, 'cac:TaxTotal')
        tax_amount_elem = SubElement(tax_total, 'cbc:TaxAmount')
        tax_amount_elem.set('currencyID', currency)
        tax_amount_elem.text = f"{data.get('tax_amount', 0):.2f}"

        # Tax Subtotal
        tax_subtotal = SubElement(tax_total, 'cac:TaxSubtotal')
        taxable_amount = SubElement(tax_subtotal, 'cbc:TaxableAmount')
        taxable_amount.set('currencyID', currency)
        taxable_amount.text = f"{data.get('subtotal', 0):.2f}"

        tax_amount_sub = SubElement(tax_subtotal, 'cbc:TaxAmount')
        tax_amount_sub.set('currencyID', currency)
        tax_amount_sub.text = f"{data.get('tax_amount', 0):.2f}"

        tax_category = SubElement(tax_subtotal, 'cac:TaxCategory')
        tax_id = SubElement(tax_category, 'cbc:ID')
        tax_id.text = 'S'  # Standard rate
        tax_percent = SubElement(tax_category, 'cbc:Percent')
        tax_percent.text = f"{data.get('tax_rate', 0.20) * 100:.0f}"

        tax_scheme = SubElement(tax_category, 'cac:TaxScheme')
        tax_scheme_id = SubElement(tax_scheme, 'cbc:ID')
        tax_scheme_id.text = 'VAT'

        # Legal Monetary Total
        monetary_total = SubElement(root, 'cac:LegalMonetaryTotal')

        line_extension = SubElement(monetary_total, 'cbc:LineExtensionAmount')
        line_extension.set('currencyID', currency)
        line_extension.text = f"{data.get('subtotal', 0):.2f}"

        tax_exclusive = SubElement(monetary_total, 'cbc:TaxExclusiveAmount')
        tax_exclusive.set('currencyID', currency)
        tax_exclusive.text = f"{data.get('subtotal', 0):.2f}"

        tax_inclusive = SubElement(monetary_total, 'cbc:TaxInclusiveAmount')
        tax_inclusive.set('currencyID', currency)
        tax_inclusive.text = f"{data.get('total', 0):.2f}"

        payable_amount = SubElement(monetary_total, 'cbc:PayableAmount')
        payable_amount.set('currencyID', currency)
        payable_amount.text = f"{data.get('total', 0):.2f}"

        # Invoice Lines
        for idx, item in enumerate(data.get('items', []), 1):
            self._add_invoice_line(root, item, idx, currency)

        return self._prettify_xml(root)

    def _add_invoice_line(self, root, item, line_id, currency):
        """Add invoice line item"""
        line = SubElement(root, 'cac:InvoiceLine')

        # Line ID
        id_elem = SubElement(line, 'cbc:ID')
        id_elem.text = str(line_id)

        # Quantity
        quantity = SubElement(line, 'cbc:InvoicedQuantity')
        quantity.set('unitCode', self._get_unit_code(item.get('unit', 'hr')))
        quantity.text = str(item.get('quantity', 1))

        # Line Extension Amount
        line_amount = SubElement(line, 'cbc:LineExtensionAmount')
        line_amount.set('currencyID', currency)
        line_amount.text = f"{item.get('total', 0):.2f}"

        # Item
        item_elem = SubElement(line, 'cac:Item')
        description = SubElement(item_elem, 'cbc:Description')
        description.text = item.get('description', '')
        name = SubElement(item_elem, 'cbc:Name')
        name.text = item.get('description', '')

        # Price
        price_elem = SubElement(line, 'cac:Price')
        price_amount = SubElement(price_elem, 'cbc:PriceAmount')
        price_amount.set('currencyID', currency)
        price_amount.text = f"{item.get('unit_price', 0):.2f}"

        return line

    def _get_unit_code(self, unit):
        """Convert unit to UN/ECE Recommendation 20 code"""
        unit_map = {
            'hr': 'HUR',  # Hour
            'hrs': 'HUR',
            'day': 'DAY',
            'pcs': 'C62',  # Piece
            'pc': 'C62',
            'kit': 'KT',
            'set': 'SET',
            'lic': 'C62',
        }
        return unit_map.get(unit.lower(), 'C62')


class OrderUBLGenerator(UBLGenerator):
    """Generate UBL 2.1 Order XML"""

    def generate(self, data, language='en-GB'):
        """Generate UBL Order XML"""
        currency = self._get_currency_code(language)

        # Update namespaces for Order
        root = Element('Order')
        root.set('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:Order-2')
        root.set('xmlns:cac', self.NAMESPACES['xmlns:cac'])
        root.set('xmlns:cbc', self.NAMESPACES['xmlns:cbc'])

        # UBL Version
        ubl_version = SubElement(root, 'cbc:UBLVersionID')
        ubl_version.text = '2.1'

        # Order ID
        order_id = SubElement(root, 'cbc:ID')
        order_id.text = data.get('order_number', 'ORD-0001')

        # Issue Date
        issue_date = SubElement(root, 'cbc:IssueDate')
        issue_date.text = self._format_date(data.get('order_date', datetime.now()))

        # Document Currency Code
        currency_code = SubElement(root, 'cbc:DocumentCurrencyCode')
        currency_code.text = currency

        # Buyer Customer Party (Company placing order)
        self._add_party(root, data.get('company', {}), 'BuyerCustomerParty')

        # Seller Supplier Party (Supplier)
        self._add_party(root, data.get('customer', {}), 'SellerSupplierParty')

        # Anticipated Monetary Total
        monetary_total = SubElement(root, 'cac:AnticipatedMonetaryTotal')

        line_extension = SubElement(monetary_total, 'cbc:LineExtensionAmount')
        line_extension.set('currencyID', currency)
        line_extension.text = f"{data.get('subtotal', 0):.2f}"

        tax_exclusive = SubElement(monetary_total, 'cbc:TaxExclusiveAmount')
        tax_exclusive.set('currencyID', currency)
        tax_exclusive.text = f"{data.get('subtotal', 0):.2f}"

        tax_inclusive = SubElement(monetary_total, 'cbc:TaxInclusiveAmount')
        tax_inclusive.set('currencyID', currency)
        tax_inclusive.text = f"{data.get('total', 0):.2f}"

        payable_amount = SubElement(monetary_total, 'cbc:PayableAmount')
        payable_amount.set('currencyID', currency)
        payable_amount.text = f"{data.get('total', 0):.2f}"

        # Order Lines
        for idx, item in enumerate(data.get('items', []), 1):
            self._add_order_line(root, item, idx, currency)

        return self._prettify_xml(root)

    def _add_order_line(self, root, item, line_id, currency):
        """Add order line item"""
        line = SubElement(root, 'cac:OrderLine')

        line_item = SubElement(line, 'cac:LineItem')

        # Line ID
        id_elem = SubElement(line_item, 'cbc:ID')
        id_elem.text = str(line_id)

        # Quantity
        quantity = SubElement(line_item, 'cbc:Quantity')
        quantity.set('unitCode', InvoiceUBLGenerator()._get_unit_code(item.get('unit', 'pcs')))
        quantity.text = str(item.get('quantity', 1))

        # Line Extension Amount
        line_amount = SubElement(line_item, 'cbc:LineExtensionAmount')
        line_amount.set('currencyID', currency)
        line_amount.text = f"{item.get('total', 0):.2f}"

        # Item
        item_elem = SubElement(line_item, 'cac:Item')
        description = SubElement(item_elem, 'cbc:Description')
        description.text = item.get('description', '')
        name = SubElement(item_elem, 'cbc:Name')
        name.text = item.get('description', '')

        # Price
        price_elem = SubElement(line_item, 'cac:Price')
        price_amount = SubElement(price_elem, 'cbc:PriceAmount')
        price_amount.set('currencyID', currency)
        price_amount.text = f"{item.get('unit_price', 0):.2f}"

        return line


class DespatchAdviceUBLGenerator(UBLGenerator):
    """Generate UBL 2.1 DespatchAdvice (Delivery Note) XML"""

    def generate(self, data, language='en-GB'):
        """Generate UBL DespatchAdvice XML"""
        currency = self._get_currency_code(language)

        # Update namespaces for DespatchAdvice
        root = Element('DespatchAdvice')
        root.set('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2')
        root.set('xmlns:cac', self.NAMESPACES['xmlns:cac'])
        root.set('xmlns:cbc', self.NAMESPACES['xmlns:cbc'])

        # UBL Version
        ubl_version = SubElement(root, 'cbc:UBLVersionID')
        ubl_version.text = '2.1'

        # Despatch Advice ID
        despatch_id = SubElement(root, 'cbc:ID')
        despatch_id.text = data.get('delivery_number', 'DN-0001')

        # Issue Date
        issue_date = SubElement(root, 'cbc:IssueDate')
        issue_date.text = self._format_date(data.get('delivery_date', datetime.now()))

        # Order Reference
        if data.get('order_number'):
            order_ref = SubElement(root, 'cac:OrderReference')
            order_id = SubElement(order_ref, 'cbc:ID')
            order_id.text = data['order_number']

        # Despatch Supplier Party (Company shipping)
        self._add_party(root, data.get('company', {}), 'DespatchSupplierParty')

        # Delivery Customer Party (Customer receiving)
        self._add_party(root, data.get('customer', {}), 'DeliveryCustomerParty')

        # Shipment
        shipment = SubElement(root, 'cac:Shipment')
        shipment_id = SubElement(shipment, 'cbc:ID')
        shipment_id.text = data.get('tracking_number', '')

        # Delivery
        delivery = SubElement(shipment, 'cac:Delivery')

        if data.get('expected_date'):
            delivery_date = SubElement(delivery, 'cbc:ActualDeliveryDate')
            delivery_date.text = self._format_date(data['expected_date'])

        # Delivery Address
        delivery_address = SubElement(delivery, 'cac:DeliveryAddress')
        customer = data.get('customer', {})
        street = SubElement(delivery_address, 'cbc:StreetName')
        street.text = customer.get('address', '')
        city = SubElement(delivery_address, 'cbc:CityName')
        city.text = customer.get('city', '')
        postal_code = SubElement(delivery_address, 'cbc:PostalZone')
        postal_code.text = customer.get('postal_code', '')

        # Despatch Lines
        for idx, item in enumerate(data.get('items', []), 1):
            self._add_despatch_line(root, item, idx)

        return self._prettify_xml(root)

    def _add_despatch_line(self, root, item, line_id):
        """Add despatch line item"""
        line = SubElement(root, 'cac:DespatchLine')

        # Line ID
        id_elem = SubElement(line, 'cbc:ID')
        id_elem.text = str(line_id)

        # Delivered Quantity
        quantity = SubElement(line, 'cbc:DeliveredQuantity')
        quantity.set('unitCode', InvoiceUBLGenerator()._get_unit_code(item.get('unit', 'pcs')))
        quantity.text = str(item.get('quantity', 1))

        # Item
        item_elem = SubElement(line, 'cac:Item')
        description = SubElement(item_elem, 'cbc:Description')
        description.text = item.get('description', '')
        name = SubElement(item_elem, 'cbc:Name')
        name.text = item.get('description', '')

        return line
