"""
Customer Order document generator
"""
import os
from datetime import datetime, timedelta
import random
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from utils.i18n import get_translation, format_date, format_currency, get_tax_rate
from utils.faker_data import get_generator


class OrderGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, customer_data=None, items=None,
                 order_number=None, order_date=None, delivery_date=None,
                 status='confirmed', output_format='pdf', output_path=None):
        """
        Generate a customer order document

        Args:
            company_data: Dict with company (seller) information
            customer_data: Dict with customer information (auto-generated if None)
            items: List of order items (auto-generated if None)
            order_number: Order number (auto-generated if None)
            order_date: Order date (defaults to today)
            delivery_date: Expected delivery date (auto-generated if None)
            status: Order status (pending, confirmed, processing, shipped)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if customer_data is None:
            customer_data = self.data_gen.generate_customer()

        if items is None:
            items = self.data_gen.generate_order_items()

        if order_number is None:
            order_number = self.data_gen.generate_document_number('order')

        if order_date is None:
            order_date = datetime.now()

        if delivery_date is None:
            delivery_date = order_date + timedelta(days=random.randint(3, 14))

        # Calculate totals
        subtotal = sum(item['total'] for item in items)
        tax_rate = get_tax_rate(self.language)
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        # Prepare document data
        doc_data = {
            'order_number': order_number,
            'order_date': order_date,
            'delivery_date': delivery_date,
            'status': status,
            'company': company_data,
            'customer': customer_data,
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
        """Generate professional PDF order"""
        if output_path is None:
            filename = f"{data['order_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'orders', filename)

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

        # Company name (left) and ORDER title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        order_title = get_translation('order', self.language).upper()
        title_width = c.stringWidth(order_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, order_title)

        y -= 6*mm

        # Company details (left) and Order number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        order_num = f"{get_translation('order_number', self.language)}: {data['order_number']}"
        num_width = c.stringWidth(order_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, order_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        date_str = format_date(data['order_date'], self.language)
        date_text = f"{get_translation('date', self.language)}: {date_str}"
        date_width = c.stringWidth(date_text, "Helvetica", 10)
        c.drawString(width - margin - date_width, y, date_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{get_translation('phone', self.language)}: {data['company']['phone']}")

        # Status (right side, colored)
        status_text = f"{get_translation('status', self.language)}: {get_translation(data['status'], self.language).upper()}"
        c.setFont("Helvetica-Bold", 10)
        status_color = HexColor('#48bb78') if data['status'] in ['confirmed', 'shipped'] else HexColor('#ed8936')
        c.setFillColor(status_color)
        status_width = c.stringWidth(status_text, "Helvetica-Bold", 10)
        c.drawString(width - margin - status_width, y, status_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, f"{get_translation('email', self.language)}: {data['company'].get('email', 'N/A')}")

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== TWO COLUMNS: SELLER & CUSTOMER =====
        col_width = (width - 2*margin - 10*mm) / 2

        # LEFT COLUMN: SELLER (FROM)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "FROM:")

        y_left = y - 5*mm
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y_left, data['company']['name'])
        y_left -= 4*mm
        c.drawString(margin, y_left, data['company']['address'])
        y_left -= 4*mm
        c.drawString(margin, y_left, f"{data['company']['postal_code']} {data['company']['city']}")
        y_left -= 4*mm
        c.drawString(margin, y_left, data['company']['country'])

        # RIGHT COLUMN: CUSTOMER (TO)
        x_right = margin + col_width + 10*mm
        c.setFont("Helvetica-Bold", 10)
        bill_to_text = get_translation('customer', self.language).upper() + ":"
        c.drawString(x_right, y, bill_to_text)

        y_right = y - 5*mm
        c.setFont("Helvetica", 9)
        c.drawString(x_right, y_right, data['customer']['name'])
        y_right -= 4*mm
        c.drawString(x_right, y_right, data['customer']['address'])
        y_right -= 4*mm
        c.drawString(x_right, y_right, f"{data['customer']['postal_code']} {data['customer']['city']}")
        y_right -= 4*mm
        c.drawString(x_right, y_right, data['customer']['country'])

        y = min(y_left, y_right) - 10*mm

        # ===== ITEMS TABLE =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, get_translation('order_items', self.language).upper())

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
        totals_x = width - margin - 60*mm

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)

        # Subtotal
        c.drawString(totals_x, y, get_translation('subtotal', self.language) + ":")
        subtotal_text = format_currency(data['subtotal'], self.language)
        subtotal_width = c.stringWidth(subtotal_text, "Helvetica", 10)
        c.drawString(width - margin - subtotal_width, y, subtotal_text)

        y -= 6*mm

        # Tax
        tax_label = get_translation('tax', self.language)
        c.drawString(totals_x, y, f"{tax_label} ({int(data['tax_rate']*100)}%):")
        tax_text = format_currency(data['tax_amount'], self.language)
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

        # ===== DELIVERY INFORMATION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "DELIVERY INFORMATION:")

        y -= 6*mm

        c.setFont("Helvetica", 9)
        delivery_text = f"Expected Delivery: {format_date(data['delivery_date'], self.language)}"
        c.drawString(margin, y, delivery_text)

        y -= 5*mm
        c.drawString(margin, y, f"Delivery Address: {data['customer']['address']}, {data['customer']['city']}")

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
        """Generate HTML order (basic implementation)"""
        if output_path is None:
            filename = f"{data['order_number'].replace('/', '-')}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'orders', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order {data['order_number']}</title>
        </head>
        <body>
            <h1>Order {data['order_number']}</h1>
            <p>Status: {data['status']}</p>
            <p>Total: {format_currency(data['total'], self.language)}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
