"""
Internationalization utilities for document generation
"""

TRANSLATIONS = {
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

def get_translation(key, language='fr'):
    """Get translation for a key in specified language"""
    return TRANSLATIONS.get(language, TRANSLATIONS['fr']).get(key, key)

def format_date(date, language='fr'):
    """Format date according to locale"""
    if language == 'fr':
        return date.strftime('%d/%m/%Y')
    elif language == 'de':
        return date.strftime('%d.%m.%Y')
    return date.strftime('%Y-%m-%d')

def format_currency(amount, language='fr'):
    """Format currency according to locale"""
    if language == 'fr':
        return f"{amount:,.2f} €".replace(',', ' ')
    elif language == 'de':
        return f"{amount:,.2f} €".replace(',', '.')
    return f"€{amount:,.2f}"

def get_tax_rate(language='fr'):
    """Get tax rate for country"""
    rates = {
        'fr': 0.20,  # 20% TVA in France
        'de': 0.19   # 19% MwSt in Germany
    }
    return rates.get(language, 0.20)
