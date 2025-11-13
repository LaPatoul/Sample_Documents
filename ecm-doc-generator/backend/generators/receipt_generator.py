"""
Receipt document generator
"""
import os
from datetime import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, colors
from ..utils.pdf_generator import PDFGenerator
from ..utils.i18n import get_translation, format_date, format_currency
from ..utils.faker_data import get_generator

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
        """Generate PDF receipt - compact design"""
        if output_path is None:
            filename = f"{data['receipt_number'].replace('/', '-')}.pdf"
            output_path = os.path.join('storage', 'receipts', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        pdf = PDFGenerator(output_path)

        # Add watermark
        watermark_text = get_translation('sample_watermark', self.language)
        pdf.add_watermark(watermark_text)

        # Compact header for receipt
        y_pos = pdf.height - 20*mm

        # Company name centered
        pdf.canvas.setFont("Helvetica-Bold", 18)
        pdf.canvas.setFillColor(HexColor('#667eea'))
        company_name_width = pdf.canvas.stringWidth(data['company']['name'], "Helvetica-Bold", 18)
        pdf.canvas.drawString((pdf.width - company_name_width) / 2, y_pos, data['company']['name'])

        y_pos -= 6*mm

        # Company details centered
        pdf.canvas.setFont("Helvetica", 9)
        pdf.canvas.setFillColor(colors.black)

        details = [
            data['company']['address'],
            f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}",
            f"Tel: {data['company']['phone']}"
        ]

        for detail in details:
            detail_width = pdf.canvas.stringWidth(detail, "Helvetica", 9)
            pdf.canvas.drawString((pdf.width - detail_width) / 2, y_pos, detail)
            y_pos -= 4*mm

        y_pos -= 5*mm

        # Receipt title and number
        pdf.canvas.setFont("Helvetica-Bold", 16)
        receipt_title = get_translation('receipt', self.language).upper()
        title_width = pdf.canvas.stringWidth(receipt_title, "Helvetica-Bold", 16)
        pdf.canvas.drawString((pdf.width - title_width) / 2, y_pos, receipt_title)

        y_pos -= 7*mm

        pdf.canvas.setFont("Helvetica", 10)
        receipt_info = f"{get_translation('receipt_number', self.language)}: {data['receipt_number']}"
        info_width = pdf.canvas.stringWidth(receipt_info, "Helvetica", 10)
        pdf.canvas.drawString((pdf.width - info_width) / 2, y_pos, receipt_info)

        y_pos -= 5*mm

        date_info = f"{get_translation('date', self.language)}: {format_date(data['receipt_date'], self.language)}"
        date_width = pdf.canvas.stringWidth(date_info, "Helvetica", 10)
        pdf.canvas.drawString((pdf.width - date_width) / 2, y_pos, date_info)

        y_pos -= 10*mm

        # Separator line
        pdf.canvas.setStrokeColor(colors.grey)
        pdf.canvas.line(pdf.margin, y_pos, pdf.width - pdf.margin, y_pos)

        y_pos -= 7*mm

        # Items
        pdf.canvas.setFont("Helvetica-Bold", 9)
        pdf.canvas.drawString(pdf.margin, y_pos, get_translation('items', self.language).upper())

        y_pos -= 7*mm

        pdf.canvas.setFont("Helvetica", 9)
        for item in data['items']:
            # Item description and quantity
            item_text = f"{item['description']} x {item['quantity']}"
            pdf.canvas.drawString(pdf.margin + 5*mm, y_pos, item_text)

            # Item total (right aligned)
            total_text = format_currency(item['total'], self.language)
            total_width = pdf.canvas.stringWidth(total_text, "Helvetica", 9)
            pdf.canvas.drawString(pdf.width - pdf.margin - total_width, y_pos, total_text)

            y_pos -= 5*mm

        y_pos -= 3*mm

        # Separator line
        pdf.canvas.setStrokeColor(colors.grey)
        pdf.canvas.line(pdf.margin, y_pos, pdf.width - pdf.margin, y_pos)

        y_pos -= 7*mm

        # Total
        pdf.canvas.setFont("Helvetica-Bold", 14)
        total_label = get_translation('total', self.language).upper()
        pdf.canvas.drawString(pdf.margin, y_pos, total_label)

        total_text = format_currency(data['total'], self.language)
        total_width = pdf.canvas.stringWidth(total_text, "Helvetica-Bold", 14)
        pdf.canvas.drawString(pdf.width - pdf.margin - total_width, y_pos, total_text)

        y_pos -= 10*mm

        # Payment method
        pdf.canvas.setFont("Helvetica", 9)
        payment_text = f"{get_translation('payment_method', self.language)}: {get_translation(data['payment_method'], self.language)}"
        payment_width = pdf.canvas.stringWidth(payment_text, "Helvetica", 9)
        pdf.canvas.drawString((pdf.width - payment_width) / 2, y_pos, payment_text)

        y_pos -= 10*mm

        # Thank you message
        pdf.canvas.setFont("Helvetica-Bold", 10)
        thank_you = get_translation('thank_you', self.language)
        thank_you_width = pdf.canvas.stringWidth(thank_you, "Helvetica-Bold", 10)
        pdf.canvas.drawString((pdf.width - thank_you_width) / 2, y_pos, thank_you)

        pdf.save()
        return output_path

    def _generate_html(self, data, output_path):
        """Generate HTML receipt"""
        if output_path is None:
            filename = f"{data['receipt_number'].replace('/', '-')}.html"
            output_path = os.path.join('storage', 'receipts', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_content = self._create_html_template(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

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
