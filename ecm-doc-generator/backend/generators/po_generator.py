"""
Purchase Order document generator
"""
import os
from datetime import datetime, timedelta
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from utils.pdf_generator import PDFGenerator
from utils.i18n import get_translation, format_date, format_currency, get_tax_rate
from utils.faker_data import get_generator

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
        """Generate professional PDF purchase order"""
        if output_path is None:
            filename = f"{data['po_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'purchase_orders', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.colors import HexColor, black, grey
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import Table, TableStyle

        c = pdf_canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        margin = 20*mm

        # ============ WATERMARK (CENTERED) ============
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
        c.translate(width/2, height/2)
        c.rotate(45)
        watermark_text = get_translation('sample_watermark', self.language)
        watermark_width = c.stringWidth(watermark_text, "Helvetica-Bold", 50)
        c.drawString(-watermark_width/2, 0, watermark_text)
        c.restoreState()

        # ============ COMPACT HEADER ============
        y = height - margin - 10*mm

        # Company name (left)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        c.drawString(margin, y, data['company']['name'])

        # PURCHASE ORDER title (right)
        doc_title = get_translation('purchase_order', self.language).upper()
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(HexColor('#2c5282'))
        title_width = c.stringWidth(doc_title, "Helvetica-Bold", 24)
        c.drawString(width - margin - title_width, y, doc_title)

        y -= 15*mm

        # Horizontal line separator
        c.setStrokeColor(HexColor('#cbd5e0'))
        c.setLineWidth(0.5)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ============ TWO COLUMNS: BUYER & VENDOR ============
        col_width = (width - 2*margin - 10*mm) / 2

        # LEFT: BUYER (Company ordering)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(black)
        c.drawString(margin, y, "BUYER:")

        c.setFont("Helvetica", 9)
        y -= 5*mm
        c.drawString(margin, y, data['company']['name'])
        y -= 4*mm
        c.drawString(margin, y, data['company']['address'])
        y -= 4*mm
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}")
        y -= 4*mm
        c.drawString(margin, y, data['company']['country'])
        y -= 4*mm
        c.drawString(margin, y, f"Tel: {data['company']['phone']}")
        y -= 4*mm
        c.drawString(margin, y, f"Email: {data['company']['email']}")

        # RIGHT: VENDOR
        y_right = height - margin - 25*mm - 10*mm
        x_right = margin + col_width + 10*mm

        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_right, y_right, get_translation('vendor', self.language).upper() + ":")

        c.setFont("Helvetica", 9)
        y_right -= 5*mm
        c.drawString(x_right, y_right, data['vendor']['name'])
        y_right -= 4*mm
        c.drawString(x_right, y_right, data['vendor']['address'])
        y_right -= 4*mm
        c.drawString(x_right, y_right, f"{data['vendor']['postal_code']} {data['vendor']['city']}")
        y_right -= 4*mm
        c.drawString(x_right, y_right, data['vendor']['country'])
        y_right -= 4*mm
        c.drawString(x_right, y_right, f"Tel: {data['vendor']['phone']}")

        # PO details (right column, below vendor)
        y_right -= 8*mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_right, y_right, f"{get_translation('po_number', self.language)}: ")
        c.setFont("Helvetica", 9)
        c.drawString(x_right + 35*mm, y_right, data['po_number'])

        y_right -= 4*mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_right, y_right, f"{get_translation('order_date', self.language)}: ")
        c.setFont("Helvetica", 9)
        c.drawString(x_right + 35*mm, y_right, format_date(data['order_date'], self.language))

        y_right -= 4*mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_right, y_right, f"{get_translation('delivery_date', self.language)}: ")
        c.setFont("Helvetica", 9)
        c.drawString(x_right + 35*mm, y_right, format_date(data['delivery_date'], self.language))

        y_right -= 4*mm
        status_text = get_translation(data['status'], self.language)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_right, y_right, f"{get_translation('status', self.language)}: ")
        c.setFillColor(HexColor('#48bb78'))  # Green for status
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_right + 35*mm, y_right, status_text)
        c.setFillColor(black)

        # Move to table position
        y = min(y - 10*mm, y_right - 15*mm)

        # ============ ITEMS TABLE ============
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

        col_widths = [85*mm, 18*mm, 15*mm, 30*mm, 27*mm]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cbd5e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),
        ]))

        table.wrapOn(c, width, height)
        table_height = table._height
        table.drawOn(c, margin, y - table_height)

        y = y - table_height - 10*mm

        # ============ TOTALS ============
        totals_width = 60*mm
        totals_x = width - margin - totals_width

        c.setFont("Helvetica", 9)
        c.setFillColor(black)

        # Subtotal
        c.drawString(totals_x, y, get_translation('subtotal', self.language) + ":")
        c.drawRightString(width - margin, y, format_currency(data['subtotal'], self.language))

        y -= 5*mm
        # Tax
        tax_label = f"{get_translation('tax', self.language)} ({int(data['tax_rate']*100)}%):"
        c.drawString(totals_x, y, tax_label)
        c.drawRightString(width - margin, y, format_currency(data['tax_amount'], self.language))

        y -= 8*mm
        # Grand total
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HexColor('#2c5282'))
        c.drawString(totals_x, y, get_translation('grand_total', self.language).upper() + ":")
        c.drawRightString(width - margin, y, format_currency(data['total'], self.language))

        # ============ DELIVERY TERMS ============
        y -= 15*mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(black)
        c.drawString(margin, y, "DELIVERY & TERMS:")

        y -= 5*mm
        c.setFont("Helvetica", 8)
        c.drawString(margin, y, f"Expected delivery: {format_date(data['delivery_date'], self.language)}")

        y -= 4*mm
        c.drawString(margin, y, "Delivery address: Same as buyer address above")

        y -= 4*mm
        c.drawString(margin, y, "Payment terms: Net 30 days from delivery date")

        # ============ FOOTER ============
        footer_y = margin + 15*mm

        # Separator line
        c.setStrokeColor(HexColor('#cbd5e0'))
        c.line(margin, footer_y + 8*mm, width - margin, footer_y + 8*mm)

        c.setFont("Helvetica", 7)
        c.setFillColor(grey)

        # Company footer info
        footer_text = f"{data['company']['name']} | VAT: {data['company'].get('tax_id', 'N/A')} | SIRET: 123 456 789 00012"
        footer_width = c.stringWidth(footer_text, "Helvetica", 7)
        c.drawString((width - footer_width)/2, footer_y + 4*mm, footer_text)

        # Address
        footer_text2 = f"{data['company']['address']}, {data['company']['postal_code']} {data['company']['city']} | {data['company']['phone']} | {data['company']['email']}"
        footer_width2 = c.stringWidth(footer_text2, "Helvetica", 7)
        c.drawString((width - footer_width2)/2, footer_y, footer_text2)

        c.save()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

    def _generate_html(self, data, output_path):
        """Generate HTML purchase order"""
        if output_path is None:
            filename = f"{data['po_number'].replace('/', '-')}.html"
            # Use absolute path to project root's storage directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'purchase_orders', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_content = self._create_html_template(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Return relative path for API
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

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
