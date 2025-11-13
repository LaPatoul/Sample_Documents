"""
Delivery Note document generator
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
from utils.i18n import get_translation, format_date, format_currency
from utils.faker_data import get_generator


class DeliveryNoteGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, customer_data=None, items=None,
                 delivery_note_number=None, order_number=None,
                 delivery_date=None, tracking_number=None,
                 carrier='Standard Shipping', output_format='pdf', output_path=None):
        """
        Generate a delivery note document

        Args:
            company_data: Dict with company (sender) information
            customer_data: Dict with customer (receiver) information
            items: List of items being delivered (auto-generated if None)
            delivery_note_number: Delivery note number (auto-generated if None)
            order_number: Related order number for linking (auto-generated if None)
            delivery_date: Delivery date (defaults to today)
            tracking_number: Shipment tracking number (auto-generated if None)
            carrier: Shipping carrier name
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

        if delivery_note_number is None:
            delivery_note_number = self.data_gen.generate_document_number('delivery_note')

        if order_number is None:
            order_number = self.data_gen.generate_document_number('order')

        if delivery_date is None:
            delivery_date = datetime.now()

        if tracking_number is None:
            tracking_number = f"TRK{random.randint(10000000, 99999999)}"

        # Prepare document data
        doc_data = {
            'delivery_note_number': delivery_note_number,
            'order_number': order_number,
            'delivery_date': delivery_date,
            'tracking_number': tracking_number,
            'carrier': carrier,
            'company': company_data,
            'customer': customer_data,
            'items': items,
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
        """Generate professional PDF delivery note"""
        if output_path is None:
            filename = f"{data['delivery_note_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'delivery_notes', filename)

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

        # Company name (left) and DELIVERY NOTE title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        delivery_title = get_translation('delivery_note', self.language).upper()
        title_width = c.stringWidth(delivery_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, delivery_title)

        y -= 6*mm

        # Company details (left) and Delivery note number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        dn_num = f"{get_translation('delivery_note_number', self.language)}: {data['delivery_note_number']}"
        num_width = c.stringWidth(dn_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, dn_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        order_ref = f"{get_translation('order_number', self.language)}: {data['order_number']}"
        order_width = c.stringWidth(order_ref, "Helvetica", 10)
        c.drawString(width - margin - order_width, y, order_ref)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{get_translation('phone', self.language)}: {data['company']['phone']}")

        c.setFont("Helvetica", 10)
        date_str = format_date(data['delivery_date'], self.language)
        date_text = f"{get_translation('date', self.language)}: {date_str}"
        date_width = c.stringWidth(date_text, "Helvetica", 10)
        c.drawString(width - margin - date_width, y, date_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{get_translation('email', self.language)}: {data['company'].get('email', 'N/A')}")

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== TWO COLUMNS: SENDER & RECEIVER =====
        col_width = (width - 2*margin - 10*mm) / 2

        # LEFT COLUMN: SENDER
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "SENDER:")

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

        # RIGHT COLUMN: RECEIVER
        x_right = margin + col_width + 10*mm
        c.setFont("Helvetica-Bold", 10)
        receiver_text = get_translation('receiver', self.language).upper() + ":"
        c.drawString(x_right, y, receiver_text)

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

        # ===== SHIPPING INFORMATION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "SHIPPING INFORMATION:")

        y -= 6*mm

        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"Carrier: {data['carrier']}")
        c.drawString(margin + 80*mm, y, f"Tracking Number: {data['tracking_number']}")

        y -= 10*mm

        # ===== ITEMS TABLE =====
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, get_translation('items_shipped', self.language).upper())

        y -= 8*mm

        # Build table data
        table_data = [[
            get_translation('description', self.language),
            get_translation('quantity', self.language),
            get_translation('weight', self.language),
            get_translation('package_number', self.language)
        ]]

        for idx, item in enumerate(data['items'], 1):
            weight = f"{random.uniform(0.5, 10):.1f} kg"
            package_num = f"PKG-{idx:03d}"
            table_data.append([
                item['description'],
                str(item['quantity']),
                weight,
                package_num
            ])

        # Create table
        col_widths = [80*mm, 30*mm, 30*mm, 30*mm]
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

        # ===== TOTAL PACKAGES =====
        total_packages = len(data['items'])
        total_weight = sum(random.uniform(0.5, 10) for _ in data['items'])

        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, f"Total Packages: {total_packages}")
        c.drawString(margin + 60*mm, y, f"Total Weight: {total_weight:.1f} kg")

        y -= 15*mm

        # ===== SIGNATURE SECTION =====
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "DELIVERY CONFIRMATION:")

        y -= 10*mm

        # Signature boxes
        box_width = 70*mm
        box_height = 20*mm

        # Carrier signature
        c.rect(margin, y - box_height, box_width, box_height)
        c.setFont("Helvetica", 8)
        c.drawString(margin + 2*mm, y - 4*mm, "Carrier Signature:")

        # Receiver signature
        c.rect(width - margin - box_width, y - box_height, box_width, box_height)
        c.drawString(width - margin - box_width + 2*mm, y - 4*mm, "Receiver Signature:")

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
        """Generate HTML delivery note (basic implementation)"""
        if output_path is None:
            filename = f"{data['delivery_note_number'].replace('/', '-')}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'delivery_notes', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Delivery Note {data['delivery_note_number']}</title>
        </head>
        <body>
            <h1>Delivery Note {data['delivery_note_number']}</h1>
            <p>Order: {data['order_number']}</p>
            <p>Tracking: {data['tracking_number']}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
