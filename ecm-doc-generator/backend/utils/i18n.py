"""
Internationalization utilities for document generation
"""

TRANSLATIONS = {
    'en-GB': {
        'invoice': 'Invoice',
        'purchase_order': 'Purchase Order',
        'receipt': 'Receipt',
        'invoice_number': 'Invoice No.',
        'po_number': 'PO No.',
        'receipt_number': 'Receipt No.',
        'date': 'Date',
        'due_date': 'Due Date',
        'order_date': 'Order Date',
        'delivery_date': 'Delivery Date',
        'bill_to': 'Bill To',
        'ship_to': 'Ship To',
        'vendor': 'Vendor',
        'description': 'Description',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'unit_price': 'Unit Price',
        'total': 'Total',
        'subtotal': 'Subtotal',
        'tax': 'VAT',
        'grand_total': 'Grand Total',
        'status': 'Status',
        'payment_method': 'Payment Method',
        'items': 'Items',
        'sample_watermark': 'SAMPLE - FOR DEMONSTRATION PURPOSES ONLY',
        'thank_you': 'Thank you for your business',
        'company_info': 'Company Information',
        'customer_info': 'Customer Information',
        'pending': 'Pending',
        'approved': 'Approved',
        'received': 'Received',
        'cash': 'Cash',
        'credit_card': 'Credit Card',
        'bank_transfer': 'Bank Transfer',
        'check': 'Cheque',
        'page': 'Page',
        'of': 'of',
    },
    'en-US': {
        'invoice': 'Invoice',
        'purchase_order': 'Purchase Order',
        'receipt': 'Receipt',
        'invoice_number': 'Invoice No.',
        'po_number': 'PO No.',
        'receipt_number': 'Receipt No.',
        'date': 'Date',
        'due_date': 'Due Date',
        'order_date': 'Order Date',
        'delivery_date': 'Delivery Date',
        'bill_to': 'Bill To',
        'ship_to': 'Ship To',
        'vendor': 'Vendor',
        'description': 'Description',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'unit_price': 'Unit Price',
        'total': 'Total',
        'subtotal': 'Subtotal',
        'tax': 'Sales Tax',
        'grand_total': 'Grand Total',
        'status': 'Status',
        'payment_method': 'Payment Method',
        'items': 'Items',
        'sample_watermark': 'SAMPLE - FOR DEMONSTRATION PURPOSES ONLY',
        'thank_you': 'Thank you for your business',
        'company_info': 'Company Information',
        'customer_info': 'Customer Information',
        'pending': 'Pending',
        'approved': 'Approved',
        'received': 'Received',
        'cash': 'Cash',
        'credit_card': 'Credit Card',
        'bank_transfer': 'Wire Transfer',
        'check': 'Check',
        'page': 'Page',
        'of': 'of',
    },
    'es': {
        'invoice': 'Factura',
        'purchase_order': 'Orden de Compra',
        'receipt': 'Recibo',
        'invoice_number': 'Nº Factura',
        'po_number': 'Nº Pedido',
        'receipt_number': 'Nº Recibo',
        'date': 'Fecha',
        'due_date': 'Fecha de Vencimiento',
        'order_date': 'Fecha del Pedido',
        'delivery_date': 'Fecha de Entrega',
        'bill_to': 'Facturar a',
        'ship_to': 'Enviar a',
        'vendor': 'Proveedor',
        'description': 'Descripción',
        'quantity': 'Cantidad',
        'unit': 'Unidad',
        'unit_price': 'Precio Unitario',
        'total': 'Total',
        'subtotal': 'Subtotal',
        'tax': 'IVA',
        'grand_total': 'Total General',
        'status': 'Estado',
        'payment_method': 'Método de Pago',
        'items': 'Artículos',
        'sample_watermark': 'MUESTRA - SOLO PARA FINES DE DEMOSTRACIÓN',
        'thank_you': 'Gracias por su confianza',
        'company_info': 'Información de la Empresa',
        'customer_info': 'Información del Cliente',
        'pending': 'Pendiente',
        'approved': 'Aprobado',
        'received': 'Recibido',
        'cash': 'Efectivo',
        'credit_card': 'Tarjeta de Crédito',
        'bank_transfer': 'Transferencia Bancaria',
        'check': 'Cheque',
        'page': 'Página',
        'of': 'de',
    },
    'fr': {
        'invoice': 'Facture',
        'purchase_order': 'Bon de Commande',
        'receipt': 'Reçu',
        'invoice_number': 'N° Facture',
        'po_number': 'N° Commande',
        'receipt_number': 'N° Reçu',
        'date': 'Date',
        'due_date': 'Date d\'échéance',
        'order_date': 'Date de commande',
        'delivery_date': 'Date de livraison',
        'bill_to': 'Facturé à',
        'ship_to': 'Livré à',
        'vendor': 'Fournisseur',
        'description': 'Description',
        'quantity': 'Quantité',
        'unit': 'Unité',
        'unit_price': 'Prix unitaire',
        'total': 'Total',
        'subtotal': 'Sous-total',
        'tax': 'TVA',
        'grand_total': 'Total TTC',
        'status': 'Statut',
        'payment_method': 'Mode de paiement',
        'items': 'Articles',
        'sample_watermark': 'ÉCHANTILLON - À DES FINS DE DÉMONSTRATION UNIQUEMENT',
        'thank_you': 'Merci pour votre confiance',
        'company_info': 'Informations entreprise',
        'customer_info': 'Informations client',
        'pending': 'En attente',
        'approved': 'Approuvé',
        'received': 'Reçu',
        'cash': 'Espèces',
        'credit_card': 'Carte bancaire',
        'bank_transfer': 'Virement bancaire',
        'check': 'Chèque',
        'page': 'Page',
        'of': 'sur',
    },
    'de': {
        'invoice': 'Rechnung',
        'purchase_order': 'Bestellung',
        'receipt': 'Quittung',
        'invoice_number': 'Rechnungsnr.',
        'po_number': 'Bestellnr.',
        'receipt_number': 'Quittungsnr.',
        'date': 'Datum',
        'due_date': 'Fälligkeitsdatum',
        'order_date': 'Bestelldatum',
        'delivery_date': 'Lieferdatum',
        'bill_to': 'Rechnung an',
        'ship_to': 'Lieferung an',
        'vendor': 'Lieferant',
        'description': 'Beschreibung',
        'quantity': 'Menge',
        'unit': 'Einheit',
        'unit_price': 'Einzelpreis',
        'total': 'Gesamt',
        'subtotal': 'Zwischensumme',
        'tax': 'MwSt',
        'grand_total': 'Gesamtbetrag',
        'status': 'Status',
        'payment_method': 'Zahlungsart',
        'items': 'Artikel',
        'sample_watermark': 'MUSTER - NUR FÜR DEMONSTRATIONSZWECKE',
        'thank_you': 'Vielen Dank für Ihr Vertrauen',
        'company_info': 'Firmeninformationen',
        'customer_info': 'Kundeninformationen',
        'pending': 'Ausstehend',
        'approved': 'Genehmigt',
        'received': 'Empfangen',
        'cash': 'Bargeld',
        'credit_card': 'Kreditkarte',
        'bank_transfer': 'Banküberweisung',
        'check': 'Scheck',
        'page': 'Seite',
        'of': 'von',
    }
}

def get_translation(key, language='en-GB'):
    """Get translation for a key in specified language"""
    return TRANSLATIONS.get(language, TRANSLATIONS['en-GB']).get(key, key)

def format_date(date, language='en-GB'):
    """Format date according to locale"""
    formats = {
        'en-GB': '%d/%m/%Y',  # 31/12/2024
        'en-US': '%m/%d/%Y',  # 12/31/2024
        'fr': '%d/%m/%Y',     # 31/12/2024
        'de': '%d.%m.%Y',     # 31.12.2024
        'es': '%d/%m/%Y',     # 31/12/2024
    }
    return date.strftime(formats.get(language, '%d/%m/%Y'))

def format_currency(amount, language='en-GB'):
    """Format currency according to locale"""
    if language == 'en-GB':
        return f"£{amount:,.2f}"
    elif language == 'en-US':
        return f"${amount:,.2f}"
    elif language == 'fr':
        return f"{amount:,.2f} €".replace(',', ' ')
    elif language == 'de':
        return f"{amount:,.2f} €".replace(',', '.')
    elif language == 'es':
        return f"{amount:,.2f} €".replace(',', '.')
    return f"£{amount:,.2f}"

def get_tax_rate(language='en-GB'):
    """Get tax rate for country"""
    rates = {
        'en-GB': 0.20,   # 20% VAT in UK
        'en-US': 0.08,   # 8% Sales Tax (average)
        'fr': 0.20,      # 20% TVA in France
        'de': 0.19,      # 19% MwSt in Germany
        'es': 0.21,      # 21% IVA in Spain
    }
    return rates.get(language, 0.20)

def get_currency_code(language='en-GB'):
    """Get currency code for language"""
    currencies = {
        'en-GB': 'GBP',
        'en-US': 'USD',
        'fr': 'EUR',
        'de': 'EUR',
        'es': 'EUR',
    }
    return currencies.get(language, 'GBP')
