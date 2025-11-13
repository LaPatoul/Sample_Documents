"""
Purchase Order document generator
"""
import os
from datetime import datetime, timedelta
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from ..utils.pdf_generator import PDFGenerator
from ..utils.i18n import get_translation, format_date, format_currency, get_tax_rate
from ..utils.faker_data import get_generator

class PurchaseOrderGenerator:
    def __init__(self, language='fr', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, vendor_data=None, items=None, po_number=None,
                 order_date=None, delivery_date=None, status='pending',
                 output_format='pdf', output_path=None):
        """
        Generate a purchase order document

        Args:
            company_data: Dict with company information
            vendor_data: Dict with vendor information (auto-generated if None)
            items: List of PO items (auto-generated if None)
            po_number: PO number (auto-generated if None)
            order_date: Order date (defaults to today)
            delivery_date: Expected delivery date (defaults to 14 days from order)
            status: Order status (pending, approved, received)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if vendor_data is None:
            vendor_data = self.data_gen.generate_company()

        if items is None:
            items = self.data_gen.generate_purchase_order_items()

        if po_number is None:
            po_number = self.data_gen.generate_document_number('purchase_order')

        if order_date is None:
            order_date = datetime.now()

        if delivery_date is None:
            delivery_date = order_date + timedelta(days=14)

        # Calculate totals
        subtotal = sum(item['total'] for item in items)
        tax_rate = get_tax_rate(self.language)
        tax_amount = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax_amount, 2)

        # Prepare document data
        doc_data = {
            'po_number': po_number,
            'order_date': order_date,
            'delivery_date': delivery_date,
            'status': status,
            'company': company_data,
            'vendor': vendor_data,
            'items': items,
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total': total,
            'language': self.language,
            'template_style': self.template_style
        }

        # Generate document
        if output_format == 'pdf':
            file_path = self._generate_pdf(doc_data, output_path)
        else:
            file_path = self._generate_html(doc_data, output_path)

        doc_data['file_path'] = file_path
        return doc_data

    def _generate_pdf(self, data, output_path):
        """Generate PDF purchase order"""
        if output_path is None:
            filename = f"{data['po_number'].replace('/', '-')}.pdf"
            output_path = os.path.join('storage', 'purchase_orders', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        pdf = PDFGenerator(output_path)

        # Add watermark
        watermark_text = get_translation('sample_watermark', self.language)
        pdf.add_watermark(watermark_text)

        # Draw header
        doc_title = get_translation('purchase_order', self.language).upper()
        if self.template_style == 'modern':
            y_pos = pdf.draw_header_modern(data['company'], doc_title, self.language)
        else:
            y_pos = pdf.draw_header_classic(data['company'], doc_title, self.language)

        y_pos -= 10*mm

        # PO info and dates (right side)
        info_width = 70*mm
        info_x = pdf.width - pdf.margin - info_width

        status_text = get_translation(data['status'], self.language)
        po_info = [
            f"{get_translation('po_number', self.language)}: {data['po_number']}",
            f"{get_translation('order_date', self.language)}: {format_date(data['order_date'], self.language)}",
            f"{get_translation('delivery_date', self.language)}: {format_date(data['delivery_date'], self.language)}",
            f"{get_translation('status', self.language)}: {status_text}"
        ]

        pdf.draw_info_box(info_x, y_pos - 35*mm, info_width, 35*mm,
                         get_translation('purchase_order', self.language).upper(), po_info)

        # Vendor info (left side)
        vendor_info = [
            data['vendor']['name'],
            data['vendor']['address'],
            f"{data['vendor']['postal_code']} {data['vendor']['city']}",
            data['vendor']['country'],
            f"Tel: {data['vendor']['phone']}"
        ]

        pdf.draw_info_box(pdf.margin, y_pos - 35*mm, info_width, 35*mm,
                         get_translation('vendor', self.language).upper(), vendor_info)

        y_pos -= 40*mm

        # Items table
        table_data = [[
            get_translation('description', self.language),
            get_translation('quantity', self.language),
            get_translation('unit', self.language),
            get_translation('unit_price', self.language),
            get_translation('total', self.language)
        ]]

        for item in data['items']:
            table_data.append([
                item['description'],
                str(item['quantity']),
                item['unit'],
                format_currency(item['unit_price'], self.language),
                format_currency(item['total'], self.language)
            ])

        col_widths = [80*mm, 20*mm, 15*mm, 30*mm, 30*mm]
        y_pos = pdf.draw_table(table_data, col_widths, pdf.margin, y_pos, self.template_style)

        y_pos -= 10*mm

        # Totals
        totals_width = 70*mm
        totals_x = pdf.width - pdf.margin - totals_width

        tax_label = f"{get_translation('tax', self.language)} ({int(data['tax_rate']*100)}%)"
        totals_data = [
            (get_translation('subtotal', self.language), format_currency(data['subtotal'], self.language), False),
            (tax_label, format_currency(data['tax_amount'], self.language), False),
            (get_translation('grand_total', self.language), format_currency(data['total'], self.language), True)
        ]

        pdf.draw_totals_box(totals_x, y_pos, totals_width, totals_data, self.language)

        pdf.save()
        return output_path

    def _generate_html(self, data, output_path):
        """Generate HTML purchase order"""
        if output_path is None:
            filename = f"{data['po_number'].replace('/', '-')}.html"
            output_path = os.path.join('storage', 'purchase_orders', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_content = self._create_html_template(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _create_html_template(self, data):
        """Create HTML content for purchase order"""
        items_html = ''
        for item in data['items']:
            items_html += f"""
                <tr>
                    <td>{item['description']}</td>
                    <td class="text-right">{item['quantity']}</td>
                    <td>{item['unit']}</td>
                    <td class="text-right">{format_currency(item['unit_price'], self.language)}</td>
                    <td class="text-right">{format_currency(item['total'], self.language)}</td>
                </tr>
            """

        tax_label = f"{get_translation('tax', self.language)} ({int(data['tax_rate']*100)}%)"
        status_text = get_translation(data['status'], self.language)

        html = f"""
        <!DOCTYPE html>
        <html lang="{self.language}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{get_translation('purchase_order', self.language)} - {data['po_number']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 210mm;
                    margin: 0 auto;
                    background: white;
                    padding: 0;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    position: relative;
                }}
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 60px;
                    font-weight: bold;
                    color: rgba(0,0,0,0.05);
                    white-space: nowrap;
                    pointer-events: none;
                    z-index: 1;
                }}
                .content {{
                    position: relative;
                    z-index: 2;
                    padding: 40px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 40px;
                    margin: 0 0 30px 0;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 28px;
                }}
                .header p {{
                    margin: 3px 0;
                    font-size: 14px;
                }}
                .doc-title {{
                    text-align: right;
                    font-size: 32px;
                    font-weight: bold;
                    margin-top: -60px;
                }}
                .info-section {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 30px;
                }}
                .info-box {{
                    background: #f7fafc;
                    border: 1px solid #e2e8f0;
                    padding: 15px;
                    width: 45%;
                }}
                .info-box h3 {{
                    margin: 0 0 10px 0;
                    font-size: 12px;
                    text-transform: uppercase;
                    color: #667eea;
                }}
                .info-box p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    background: #48bb78;
                    color: white;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-top: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                tr:nth-child(even) {{
                    background: #f7fafc;
                }}
                .text-right {{
                    text-align: right;
                }}
                .totals {{
                    width: 300px;
                    margin-left: auto;
                    margin-top: 20px;
                }}
                .totals-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .totals-row.grand-total {{
                    background: #667eea;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 5px;
                }}
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="watermark">{get_translation('sample_watermark', self.language)}</div>
                <div class="header">
                    <h1>{data['company']['name']}</h1>
                    <p>{data['company']['address']}</p>
                    <p>{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}</p>
                    <p>Tel: {data['company']['phone']} | Email: {data['company']['email']}</p>
                    <div class="doc-title">{get_translation('purchase_order', self.language).upper()}</div>
                </div>
                <div class="content">
                    <div class="info-section">
                        <div class="info-box">
                            <h3>{get_translation('vendor', self.language)}</h3>
                            <p><strong>{data['vendor']['name']}</strong></p>
                            <p>{data['vendor']['address']}</p>
                            <p>{data['vendor']['postal_code']} {data['vendor']['city']}</p>
                            <p>{data['vendor']['country']}</p>
                            <p>Tel: {data['vendor']['phone']}</p>
                        </div>
                        <div class="info-box">
                            <h3>{get_translation('purchase_order', self.language).upper()}</h3>
                            <p><strong>{get_translation('po_number', self.language)}:</strong> {data['po_number']}</p>
                            <p><strong>{get_translation('order_date', self.language)}:</strong> {format_date(data['order_date'], self.language)}</p>
                            <p><strong>{get_translation('delivery_date', self.language)}:</strong> {format_date(data['delivery_date'], self.language)}</p>
                            <p><strong>{get_translation('status', self.language)}:</strong> <span class="status-badge">{status_text}</span></p>
                        </div>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>{get_translation('description', self.language)}</th>
                                <th class="text-right">{get_translation('quantity', self.language)}</th>
                                <th>{get_translation('unit', self.language)}</th>
                                <th class="text-right">{get_translation('unit_price', self.language)}</th>
                                <th class="text-right">{get_translation('total', self.language)}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    <div class="totals">
                        <div class="totals-row">
                            <span>{get_translation('subtotal', self.language)}</span>
                            <span>{format_currency(data['subtotal'], self.language)}</span>
                        </div>
                        <div class="totals-row">
                            <span>{tax_label}</span>
                            <span>{format_currency(data['tax_amount'], self.language)}</span>
                        </div>
                        <div class="totals-row grand-total">
                            <span>{get_translation('grand_total', self.language)}</span>
                            <span>{format_currency(data['total'], self.language)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
