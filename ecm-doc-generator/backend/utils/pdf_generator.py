"""
PDF generation utilities using ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, grey
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

class PDFGenerator:
    def __init__(self, file_path, page_size=A4):
        self.file_path = file_path
        self.page_size = page_size
        self.width, self.height = page_size
        self.canvas = canvas.Canvas(file_path, pagesize=page_size)
        self.margin = 20 * mm

    def add_watermark(self, text):
        """Add diagonal watermark to page"""
        self.canvas.saveState()
        self.canvas.setFont("Helvetica-Bold", 50)
        self.canvas.setFillColor(grey, alpha=0.1)
        self.canvas.translate(self.width/2, self.height/2)
        self.canvas.rotate(45)
        self.canvas.drawCentredString(0, 0, text)
        self.canvas.restoreState()

    def draw_header_modern(self, company_info, doc_title, language='fr'):
        """Draw modern header with gradient effect (simulated)"""
        # Background gradient effect (simulated with rectangles)
        self.canvas.setFillColor(HexColor('#667eea'))
        self.canvas.rect(0, self.height - 80*mm, self.width, 80*mm, fill=1, stroke=0)

        # Company name
        self.canvas.setFillColor(colors.white)
        self.canvas.setFont("Helvetica-Bold", 24)
        self.canvas.drawString(self.margin, self.height - 40*mm, company_info['name'])

        # Company details
        self.canvas.setFont("Helvetica", 10)
        y_pos = self.height - 50*mm
        self.canvas.drawString(self.margin, y_pos, company_info['address'])
        y_pos -= 4*mm
        self.canvas.drawString(self.margin, y_pos, f"{company_info['postal_code']} {company_info['city']}, {company_info['country']}")
        y_pos -= 4*mm
        self.canvas.drawString(self.margin, y_pos, f"Tel: {company_info['phone']} | Email: {company_info['email']}")

        # Document title on right
        self.canvas.setFont("Helvetica-Bold", 28)
        title_width = self.canvas.stringWidth(doc_title, "Helvetica-Bold", 28)
        self.canvas.drawString(self.width - self.margin - title_width, self.height - 40*mm, doc_title)

        return self.height - 90*mm  # Return Y position for next section

    def draw_header_classic(self, company_info, doc_title, language='fr'):
        """Draw classic header with border"""
        # Border
        self.canvas.setStrokeColor(colors.black)
        self.canvas.setLineWidth(1)
        self.canvas.rect(self.margin, self.height - 70*mm, self.width - 2*self.margin, 60*mm, fill=0, stroke=1)

        # Company name
        self.canvas.setFillColor(colors.black)
        self.canvas.setFont("Helvetica-Bold", 20)
        self.canvas.drawString(self.margin + 5*mm, self.height - 20*mm, company_info['name'])

        # Company details
        self.canvas.setFont("Helvetica", 9)
        y_pos = self.height - 28*mm
        self.canvas.drawString(self.margin + 5*mm, y_pos, company_info['address'])
        y_pos -= 4*mm
        self.canvas.drawString(self.margin + 5*mm, y_pos, f"{company_info['postal_code']} {company_info['city']}, {company_info['country']}")
        y_pos -= 4*mm
        self.canvas.drawString(self.margin + 5*mm, y_pos, f"Tel: {company_info['phone']}")
        y_pos -= 4*mm
        self.canvas.drawString(self.margin + 5*mm, y_pos, f"Email: {company_info['email']}")

        # Document title
        self.canvas.setFont("Helvetica-Bold", 24)
        title_width = self.canvas.stringWidth(doc_title, "Helvetica-Bold", 24)
        self.canvas.drawString(self.width - self.margin - title_width - 5*mm, self.height - 25*mm, doc_title)

        return self.height - 75*mm

    def draw_info_box(self, x, y, width, height, title, content_lines):
        """Draw an information box"""
        self.canvas.setStrokeColor(colors.grey)
        self.canvas.setFillColor(HexColor('#f7fafc'))
        self.canvas.rect(x, y, width, height, fill=1, stroke=1)

        # Title
        self.canvas.setFillColor(colors.black)
        self.canvas.setFont("Helvetica-Bold", 11)
        self.canvas.drawString(x + 3*mm, y + height - 7*mm, title)

        # Content
        self.canvas.setFont("Helvetica", 9)
        y_pos = y + height - 14*mm
        for line in content_lines:
            self.canvas.drawString(x + 3*mm, y_pos, line)
            y_pos -= 4*mm

    def draw_table(self, data, col_widths, x, y, style='modern'):
        """Draw a table with data"""
        table = Table(data, colWidths=col_widths)

        if style == 'modern':
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),
            ]))
        else:  # classic
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

        table.wrapOn(self.canvas, self.width, self.height)
        table.drawOn(self.canvas, x, y)

        return y - table._height

    def draw_totals_box(self, x, y, width, totals_data, language='fr'):
        """Draw totals box"""
        line_height = 7*mm
        box_height = len(totals_data) * line_height + 4*mm

        self.canvas.setStrokeColor(colors.grey)
        self.canvas.setLineWidth(0.5)

        y_pos = y
        for label, amount, is_total in totals_data:
            if is_total:
                self.canvas.setFillColor(HexColor('#667eea'))
                self.canvas.rect(x, y_pos - line_height, width, line_height, fill=1, stroke=0)
                self.canvas.setFillColor(colors.white)
                self.canvas.setFont("Helvetica-Bold", 12)
            else:
                self.canvas.setFillColor(colors.black)
                self.canvas.setFont("Helvetica", 10)

            self.canvas.drawString(x + 3*mm, y_pos - 5*mm, label)
            amount_str = str(amount)
            amount_width = self.canvas.stringWidth(amount_str, self.canvas._fontname, self.canvas._fontsize)
            self.canvas.drawString(x + width - amount_width - 3*mm, y_pos - 5*mm, amount_str)

            if not is_total:
                self.canvas.setStrokeColor(colors.grey)
                self.canvas.line(x, y_pos - line_height, x + width, y_pos - line_height)

            y_pos -= line_height

        return y_pos

    def save(self):
        """Save the PDF"""
        self.canvas.save()
