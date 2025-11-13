"""
Expense Report document generator
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


class ExpenseReportGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, employee_data=None, report_number=None,
                 report_date=None, period_start=None, period_end=None,
                 expenses=None, status='submitted',
                 output_format='pdf', output_path=None):
        """
        Generate an expense report document

        Args:
            company_data: Dict with company information
            employee_data: Dict with employee information (auto-generated if None)
            report_number: Report number (auto-generated if None)
            report_date: Report submission date (defaults to today)
            period_start: Start of expense period
            period_end: End of expense period
            expenses: List of expense items (auto-generated if None)
            status: Report status (submitted, approved, rejected, reimbursed)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if employee_data is None:
            employee_data = self._generate_employee_data()

        if report_number is None:
            report_number = self.data_gen.generate_document_number('expense')

        if report_date is None:
            report_date = datetime.now()

        if period_end is None:
            period_end = report_date - timedelta(days=1)

        if period_start is None:
            period_start = period_end - timedelta(days=30)

        if expenses is None:
            expenses = self._generate_expenses(period_start, period_end)

        # Calculate total
        total = sum(exp['amount'] for exp in expenses)

        # Prepare document data
        doc_data = {
            'report_number': report_number,
            'report_date': report_date,
            'period_start': period_start,
            'period_end': period_end,
            'status': status,
            'company': company_data,
            'employee': employee_data,
            'expenses': expenses,
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

    def _generate_employee_data(self):
        """Generate random employee data"""
        return {
            'name': self.data_gen.fake.name(),
            'employee_id': f"EMP{random.randint(1000, 9999)}",
            'department': random.choice([
                'Engineering', 'Sales', 'Marketing', 'Human Resources',
                'Finance', 'Operations', 'Customer Service'
            ]),
            'email': self.data_gen.fake.email()
        }

    def _generate_expenses(self, start_date, end_date):
        """Generate random expense items"""
        expense_categories = [
            ('Travel - Flight', 150, 800),
            ('Travel - Train', 30, 200),
            ('Travel - Taxi', 10, 60),
            ('Accommodation - Hotel', 80, 250),
            ('Meals - Business Lunch', 15, 80),
            ('Meals - Business Dinner', 25, 120),
            ('Office Supplies', 10, 100),
            ('Client Entertainment', 50, 300),
            ('Conference Registration', 200, 1000),
            ('Parking', 5, 30),
            ('Fuel', 30, 150),
            ('Phone/Internet', 20, 100),
            ('Software/Subscriptions', 10, 200)
        ]

        num_expenses = random.randint(5, 15)
        expenses = []

        current_date = start_date
        for i in range(num_expenses):
            category, min_amount, max_amount = random.choice(expense_categories)

            # Generate date within period
            days_range = (end_date - start_date).days
            if days_range > 0:
                expense_date = start_date + timedelta(days=random.randint(0, days_range))
            else:
                expense_date = start_date

            expense = {
                'date': expense_date,
                'category': category,
                'description': f"{category} - {self.data_gen.fake.company()}",
                'amount': round(random.uniform(min_amount, max_amount), 2),
                'receipt_number': f"RCP-{random.randint(10000, 99999)}"
            }
            expenses.append(expense)

        # Sort by date
        expenses.sort(key=lambda x: x['date'])
        return expenses

    def _generate_pdf(self, data, output_path):
        """Generate professional PDF expense report"""
        if output_path is None:
            filename = f"{data['report_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'expense_reports', filename)

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

        # Company name (left) and EXPENSE REPORT title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        expense_title = get_translation('expense_report', self.language).upper()
        title_width = c.stringWidth(expense_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, expense_title)

        y -= 6*mm

        # Company details (left) and Report number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        report_num = f"{get_translation('report_number', self.language)}: {data['report_number']}"
        num_width = c.stringWidth(report_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, report_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        period_start_str = format_date(data['period_start'], self.language)
        period_end_str = format_date(data['period_end'], self.language)
        period_text = f"Period: {period_start_str} - {period_end_str}"
        period_width = c.stringWidth(period_text, "Helvetica", 10)
        c.drawString(width - margin - period_width, y, period_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"VAT: {data['company'].get('tax_id', 'N/A')}")

        # Status (colored)
        status_text = f"{get_translation('status', self.language)}: {get_translation(data['status'], self.language).upper()}"
        c.setFont("Helvetica-Bold", 10)

        if data['status'] == 'approved':
            status_color = HexColor('#48bb78')
        elif data['status'] == 'rejected':
            status_color = HexColor('#f56565')
        elif data['status'] == 'reimbursed':
            status_color = HexColor('#4299e1')
        else:
            status_color = HexColor('#ed8936')

        c.setFillColor(status_color)
        status_width = c.stringWidth(status_text, "Helvetica-Bold", 10)
        c.drawString(width - margin - status_width, y, status_text)

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== EMPLOYEE INFORMATION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "EMPLOYEE INFORMATION:")

        y -= 6*mm

        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"Name: {data['employee']['name']}")
        c.drawString(margin + 80*mm, y, f"Employee ID: {data['employee']['employee_id']}")

        y -= 5*mm
        c.drawString(margin, y, f"Department: {data['employee']['department']}")
        c.drawString(margin + 80*mm, y, f"Email: {data['employee']['email']}")

        y -= 10*mm

        # ===== EXPENSES TABLE =====
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "EXPENSE DETAILS:")

        y -= 8*mm

        # Build table data
        table_data = [[
            get_translation('date', self.language),
            get_translation('category', self.language),
            get_translation('description', self.language),
            get_translation('receipt', self.language),
            get_translation('amount', self.language)
        ]]

        for expense in data['expenses']:
            table_data.append([
                format_date(expense['date'], self.language),
                expense['category'],
                expense['description'][:40] + '...' if len(expense['description']) > 40 else expense['description'],
                expense['receipt_number'],
                format_currency(expense['amount'], self.language)
            ])

        # Create table
        col_widths = [25*mm, 30*mm, 60*mm, 25*mm, 30*mm]
        table = Table(table_data, colWidths=col_widths)

        # Table style
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),

            # Data rows
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('ALIGN', (0, 1), (3, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        # Draw table
        table_width, table_height = table.wrap(0, 0)

        # Check if table fits on page
        if y - table_height < 60*mm:
            # Start new page
            c.showPage()
            y = height - margin

            # Redraw watermark on new page
            c.saveState()
            c.setFont("Helvetica-Bold", 50)
            c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
            c.translate(width/2, height/2)
            c.rotate(45)
            c.drawString(-watermark_width/2, 0, watermark_text)
            c.restoreState()

        table.drawOn(c, margin, y - table_height)
        y -= table_height + 10*mm

        # ===== TOTAL =====
        totals_x = width - margin - 60*mm

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(dark_blue)
        c.drawString(totals_x, y, get_translation('total', self.language).upper() + ":")
        total_text = format_currency(data['total'], self.language)
        total_width = c.stringWidth(total_text, "Helvetica-Bold", 12)
        c.drawString(width - margin - total_width, y, total_text)

        y -= 15*mm

        # ===== APPROVAL SECTION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "APPROVAL:")

        y -= 10*mm

        # Signature boxes
        box_width = 70*mm

        c.setFont("Helvetica", 8)
        c.drawString(margin, y, "Employee Declaration:")
        c.drawString(margin, y - 4*mm, "I certify that the above expenses are accurate")
        y -= 10*mm
        c.line(margin, y, margin + box_width, y)
        c.drawString(margin, y - 4*mm, "Employee Signature & Date")

        y_manager = y + 14*mm
        c.drawString(width - margin - box_width, y_manager, "Manager Approval:")
        c.drawString(width - margin - box_width, y_manager - 4*mm, "Approved for reimbursement")
        y_manager -= 10*mm
        c.line(width - margin - box_width, y_manager, width - margin, y_manager)
        c.drawString(width - margin - box_width, y_manager - 4*mm, "Manager Signature & Date")

        # ===== FOOTER =====
        footer_y = 20*mm
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)

        footer_text = f"{data['company']['name']} | "
        footer_text += f"VAT: {data['company'].get('tax_id', 'N/A')} | "
        footer_text += f"{data['company']['address']}, {data['company']['city']}"

        footer_width = c.stringWidth(footer_text, "Helvetica", 8)
        c.drawString((width - footer_width) / 2, footer_y, footer_text)

        # Save PDF
        c.save()

        # Return relative path for API
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

    def _generate_html(self, data, output_path):
        """Generate HTML expense report (basic implementation)"""
        if output_path is None:
            filename = f"{data['report_number'].replace('/', '-')}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'expense_reports', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Expense Report {data['report_number']}</title>
        </head>
        <body>
            <h1>Expense Report {data['report_number']}</h1>
            <p>Employee: {data['employee']['name']}</p>
            <p>Total: {format_currency(data['total'], self.language)}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
