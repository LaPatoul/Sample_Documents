"""
Receipt document generator
"""
import os
from datetime import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from utils.pdf_generator import PDFGenerator
from utils.i18n import get_translation, format_date, format_currency
from utils.faker_data import get_generator

class ReceiptGenerator:
    def __init__(self, language='fr', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, items=None, receipt_number=None,
                 receipt_date=None, payment_method='cash',
                 output_format='pdf', output_path=None):
        """
        Generate a receipt document

        Args:
            company_data: Dict with company information
            items: List of receipt items (auto-generated if None)
            receipt_number: Receipt number (auto-generated if None)
            receipt_date: Receipt date (defaults to today)
            payment_method: Payment method (cash, credit_card, bank_transfer, check)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if items is None:
            items = self.data_gen.generate_receipt_items()

        if receipt_number is None:
            receipt_number = self.data_gen.generate_document_number('receipt')

        if receipt_date is None:
            receipt_date = datetime.now()

        # Calculate total
        total = sum(item['total'] for item in items)

        # Prepare document data
        doc_data = {
            'receipt_number': receipt_number,
            'receipt_date': receipt_date,
            'payment_method': payment_method,
            'company': company_data,
            'items': items,
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
        """Generate professional PDF receipt"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.platypus import Table, TableStyle

        if output_path is None:
            filename = f"{data['receipt_number'].replace('/', '-')}.pdf"
            # Use absolute path to project root's storage directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'receipts', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create canvas
        c = pdf_canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        margin = 20*mm

        # Professional dark blue color
        dark_blue = HexColor('#2c5282')

        # ===== WATERMARK (CENTERED AT 45°) =====
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
        c.translate(width/2, height/2)
        c.rotate(45)
        watermark_text = get_translation('sample_watermark', self.language)
        watermark_width = c.stringWidth(watermark_text, "Helvetica-Bold", 50)
        c.drawString(-watermark_width/2, 0, watermark_text)
        c.restoreState()

        # ===== HEADER =====
        y = height - margin

        # Company name (left) and RECEIPT title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        receipt_title = get_translation('receipt', self.language).upper()
        title_width = c.stringWidth(receipt_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, receipt_title)

        y -= 6*mm

        # Company details (left) and Receipt number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        receipt_num = f"{get_translation('receipt_number', self.language)}: {data['receipt_number']}"
        num_width = c.stringWidth(receipt_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, receipt_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        date_str = format_date(data['receipt_date'], self.language)
        date_text = f"{get_translation('date', self.language)}: {date_str}"
        date_width = c.stringWidth(date_text, "Helvetica", 10)
        c.drawString(width - margin - date_width, y, date_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{get_translation('phone', self.language)}: {data['company']['phone']}")

        y -= 4*mm
        c.drawString(margin, y, f"{get_translation('email', self.language)}: {data['company'].get('email', 'N/A')}")

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== ITEMS TABLE =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, get_translation('items', self.language).upper())

        y -= 8*mm

        # Build table data
        table_data = [[
            get_translation('description', self.language),
            get_translation('quantity', self.language),
            get_translation('unit_price', self.language),
            get_translation('amount', self.language)
        ]]

        for item in data['items']:
            table_data.append([
                item['description'],
                str(item['quantity']),
                format_currency(item['unit_price'], self.language),
                format_currency(item['total'], self.language)
            ])

        # Create table
        col_widths = [85*mm, 25*mm, 30*mm, 30*mm]
        table = Table(table_data, colWidths=col_widths)

        # Table style
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        # Draw table
        table_width, table_height = table.wrap(0, 0)
        table.drawOn(c, margin, y - table_height)

        y -= table_height + 10*mm

        # ===== TOTALS SECTION =====
        # Subtotal, tax, and total
        subtotal = data['total'] / (1 + get_translation('tax_rate', self.language))
        tax = data['total'] - subtotal

        totals_x = width - margin - 60*mm

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)

        # Subtotal
        c.drawString(totals_x, y, get_translation('subtotal', self.language) + ":")
        subtotal_text = format_currency(subtotal, self.language)
        subtotal_width = c.stringWidth(subtotal_text, "Helvetica", 10)
        c.drawString(width - margin - subtotal_width, y, subtotal_text)

        y -= 6*mm

        # Tax
        tax_label = get_translation('tax', self.language)
        c.drawString(totals_x, y, f"{tax_label}:")
        tax_text = format_currency(tax, self.language)
        tax_width = c.stringWidth(tax_text, "Helvetica", 10)
        c.drawString(width - margin - tax_width, y, tax_text)

        y -= 8*mm

        # Total line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(totals_x, y, width - margin, y)

        y -= 7*mm

        # Total amount
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(dark_blue)
        c.drawString(totals_x, y, get_translation('total', self.language).upper() + ":")
        total_text = format_currency(data['total'], self.language)
        total_width = c.stringWidth(total_text, "Helvetica-Bold", 12)
        c.drawString(width - margin - total_width, y, total_text)

        y -= 12*mm

        # ===== PAYMENT INFORMATION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "PAYMENT INFORMATION:")

        y -= 6*mm

        c.setFont("Helvetica", 9)
        payment_method_label = get_translation('payment_method', self.language)
        payment_method_text = get_translation(data['payment_method'], self.language)
        c.drawString(margin, y, f"{payment_method_label}: {payment_method_text}")

        y -= 5*mm
        c.drawString(margin, y, f"Receipt Date: {format_date(data['receipt_date'], self.language)}")

        y -= 10*mm

        # Thank you message
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(dark_blue)
        thank_you = get_translation('thank_you', self.language)
        thank_you_width = c.stringWidth(thank_you, "Helvetica-Bold", 11)
        c.drawString((width - thank_you_width) / 2, y, thank_you)

        # ===== FOOTER =====
        footer_y = 20*mm
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)

        footer_text = f"{data['company']['name']} | "
        footer_text += f"VAT: {data['company'].get('tax_id', 'N/A')} | "
        footer_text += f"SIRET: 123 456 789 00012 | "
        footer_text += f"{data['company']['address']}, {data['company']['city']}"

        footer_width = c.stringWidth(footer_text, "Helvetica", 8)
        c.drawString((width - footer_width) / 2, footer_y, footer_text)

        # Save PDF
        c.save()

        # Return relative path for API
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

    def _generate_html(self, data, output_path):
        """Generate HTML receipt"""
        if output_path is None:
            filename = f"{data['receipt_number'].replace('/', '-')}.html"
            # Use absolute path to project root's storage directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'receipts', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_content = self._create_html_template(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Return relative path for API
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

    def _create_html_template(self, data):
        """Create HTML content for receipt"""
        items_html = ''
        for item in data['items']:
            items_html += f"""
                <div class="receipt-item">
                    <div>{item['description']} x {item['quantity']}</div>
                    <div class="item-price">{format_currency(item['total'], self.language)}</div>
                </div>
            """

        payment_method_text = get_translation(data['payment_method'], self.language)

        html = f"""
        <!DOCTYPE html>
        <html lang="{self.language}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{get_translation('receipt', self.language)} - {data['receipt_number']}</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 80mm;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    position: relative;
                }}
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 30px;
                    font-weight: bold;
                    color: rgba(0,0,0,0.03);
                    white-space: nowrap;
                    pointer-events: none;
                    z-index: 1;
                }}
                .content {{
                    position: relative;
                    z-index: 2;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 2px dashed #667eea;
                }}
                .company-name {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 8px;
                }}
                .company-details {{
                    font-size: 11px;
                    color: #666;
                    line-height: 1.5;
                }}
                .receipt-title {{
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .receipt-info {{
                    text-align: center;
                    font-size: 12px;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px dashed #ccc;
                }}
                .items-section {{
                    margin: 20px 0;
                }}
                .section-title {{
                    font-weight: bold;
                    font-size: 11px;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    color: #333;
                }}
                .receipt-item {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    font-size: 12px;
                }}
                .item-price {{
                    font-weight: bold;
                }}
                .total-section {{
                    margin-top: 15px;
                    padding-top: 15px;
                    border-top: 2px solid #333;
                }}
                .total {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .payment-info {{
                    text-align: center;
                    font-size: 11px;
                    margin: 15px 0;
                    color: #666;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 2px dashed #667eea;
                    font-weight: bold;
                    font-size: 12px;
                    color: #667eea;
                }}
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        max-width: 80mm;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="watermark">{get_translation('sample_watermark', self.language)}</div>
                <div class="content">
                    <div class="header">
                        <div class="company-name">{data['company']['name']}</div>
                        <div class="company-details">
                            {data['company']['address']}<br>
                            {data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}<br>
                            Tel: {data['company']['phone']}
                        </div>
                    </div>

                    <div class="receipt-title">{get_translation('receipt', self.language).upper()}</div>

                    <div class="receipt-info">
                        {get_translation('receipt_number', self.language)}: {data['receipt_number']}<br>
                        {get_translation('date', self.language)}: {format_date(data['receipt_date'], self.language)}
                    </div>

                    <div class="items-section">
                        <div class="section-title">{get_translation('items', self.language)}</div>
                        {items_html}
                    </div>

                    <div class="total-section">
                        <div class="total">
                            <span>{get_translation('total', self.language).upper()}</span>
                            <span>{format_currency(data['total'], self.language)}</span>
                        </div>
                    </div>

                    <div class="payment-info">
                        {get_translation('payment_method', self.language)}: {payment_method_text}
                    </div>

                    <div class="footer">
                        {get_translation('thank_you', self.language)}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
