"""
Pay Slip document generator
"""
import os
from datetime import datetime
import random
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from utils.i18n import get_translation, format_date, format_currency
from utils.faker_data import get_generator


class PayslipGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, employee_data=None, payslip_number=None,
                 pay_period_start=None, pay_period_end=None,
                 pay_date=None, gross_salary=None,
                 output_format='pdf', output_path=None):
        """
        Generate a pay slip document

        Args:
            company_data: Dict with company information
            employee_data: Dict with employee information (auto-generated if None)
            payslip_number: Pay slip number (auto-generated if None)
            pay_period_start: Start of pay period
            pay_period_end: End of pay period
            pay_date: Payment date
            gross_salary: Gross salary amount (auto-generated if None)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if employee_data is None:
            employee_data = self._generate_employee_data()

        if payslip_number is None:
            payslip_number = self.data_gen.generate_document_number('payslip')

        if pay_period_end is None:
            pay_period_end = datetime.now()

        if pay_period_start is None:
            pay_period_start = datetime(pay_period_end.year, pay_period_end.month, 1)

        if pay_date is None:
            pay_date = pay_period_end

        if gross_salary is None:
            gross_salary = random.randint(2500, 8000)

        # Calculate deductions and net salary
        social_security = gross_salary * 0.22  # Social security contribution
        income_tax = gross_salary * 0.15  # Income tax
        pension = gross_salary * 0.05  # Pension contribution
        health_insurance = gross_salary * 0.03  # Health insurance

        total_deductions = social_security + income_tax + pension + health_insurance
        net_salary = gross_salary - total_deductions

        # Prepare document data
        doc_data = {
            'payslip_number': payslip_number,
            'pay_period_start': pay_period_start,
            'pay_period_end': pay_period_end,
            'pay_date': pay_date,
            'company': company_data,
            'employee': employee_data,
            'gross_salary': gross_salary,
            'deductions': {
                'social_security': social_security,
                'income_tax': income_tax,
                'pension': pension,
                'health_insurance': health_insurance,
            },
            'total_deductions': total_deductions,
            'net_salary': net_salary,
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
            'position': random.choice([
                'Software Engineer', 'Project Manager', 'Sales Representative',
                'Marketing Specialist', 'HR Manager', 'Accountant',
                'Product Designer', 'Business Analyst'
            ]),
            'department': random.choice([
                'Engineering', 'Sales', 'Marketing', 'Human Resources',
                'Finance', 'Operations', 'Customer Service'
            ]),
            'hire_date': self.data_gen.fake.date_between(start_date='-5y', end_date='-1y'),
            'social_security_number': self.data_gen.fake.ssn() if hasattr(self.data_gen.fake, 'ssn') else f"{random.randint(100000000, 999999999)}"
        }

    def _generate_pdf(self, data, output_path):
        """Generate professional PDF payslip"""
        if output_path is None:
            filename = f"{data['payslip_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'payslips', filename)

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

        # Company name (left) and PAYSLIP title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        payslip_title = get_translation('payslip', self.language).upper()
        title_width = c.stringWidth(payslip_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, payslip_title)

        y -= 6*mm

        # Company details (left) and Payslip number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        ps_num = f"{get_translation('payslip_number', self.language)}: {data['payslip_number']}"
        num_width = c.stringWidth(ps_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, ps_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        period_start = format_date(data['pay_period_start'], self.language)
        period_end = format_date(data['pay_period_end'], self.language)
        period_text = f"Period: {period_start} - {period_end}"
        period_width = c.stringWidth(period_text, "Helvetica", 10)
        c.drawString(width - margin - period_width, y, period_text)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"VAT: {data['company'].get('tax_id', 'N/A')}")

        c.setFont("Helvetica", 10)
        pay_date_str = format_date(data['pay_date'], self.language)
        pay_date_text = f"Pay Date: {pay_date_str}"
        pay_date_width = c.stringWidth(pay_date_text, "Helvetica", 10)
        c.drawString(width - margin - pay_date_width, y, pay_date_text)

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== EMPLOYEE INFORMATION =====
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "EMPLOYEE INFORMATION:")

        y -= 7*mm

        # Employee details in two columns
        c.setFont("Helvetica", 9)
        col1_x = margin
        col2_x = margin + 90*mm

        c.drawString(col1_x, y, f"Name: {data['employee']['name']}")
        c.drawString(col2_x, y, f"Employee ID: {data['employee']['employee_id']}")

        y -= 5*mm
        c.drawString(col1_x, y, f"Position: {data['employee']['position']}")
        c.drawString(col2_x, y, f"Department: {data['employee']['department']}")

        y -= 5*mm
        hire_date_str = format_date(data['employee']['hire_date'], self.language)
        c.drawString(col1_x, y, f"Hire Date: {hire_date_str}")
        c.drawString(col2_x, y, f"SSN: {data['employee']['social_security_number']}")

        y -= 10*mm

        # ===== EARNINGS AND DEDUCTIONS TABLE =====
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "EARNINGS AND DEDUCTIONS:")

        y -= 8*mm

        # Build table data
        table_data = [[
            'Description',
            'Amount'
        ]]

        # Earnings section
        table_data.append([
            'Gross Salary',
            format_currency(data['gross_salary'], self.language)
        ])

        # Deductions section
        table_data.append([
            'Deductions:',
            ''
        ])
        table_data.append([
            '  Social Security',
            f"-{format_currency(data['deductions']['social_security'], self.language)}"
        ])
        table_data.append([
            '  Income Tax',
            f"-{format_currency(data['deductions']['income_tax'], self.language)}"
        ])
        table_data.append([
            '  Pension Contribution',
            f"-{format_currency(data['deductions']['pension'], self.language)}"
        ])
        table_data.append([
            '  Health Insurance',
            f"-{format_currency(data['deductions']['health_insurance'], self.language)}"
        ])

        # Total deductions
        table_data.append([
            'Total Deductions',
            f"-{format_currency(data['total_deductions'], self.language)}"
        ])

        # Net salary
        table_data.append([
            'NET SALARY',
            format_currency(data['net_salary'], self.language)
        ])

        # Create table
        col_widths = [120*mm, 50*mm]
        table = Table(table_data, colWidths=col_widths)

        # Table style
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Gross salary row
            ('FONT', (0, 1), (-1, 1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, 1), (-1, 1), HexColor('#e6f7ff')),
            ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
            ('TOPPADDING', (0, 1), (-1, 1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 6),

            # Deductions header
            ('FONT', (0, 2), (0, 2), 'Helvetica-Bold', 9),
            ('BACKGROUND', (0, 2), (-1, 2), HexColor('#fff3cd')),
            ('TOPPADDING', (0, 2), (-1, 2), 6),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 6),

            # Deduction items
            ('FONT', (0, 3), (-1, 6), 'Helvetica', 9),
            ('ALIGN', (1, 3), (1, 6), 'RIGHT'),
            ('TOPPADDING', (0, 3), (-1, 6), 4),
            ('BOTTOMPADDING', (0, 3), (-1, 6), 4),

            # Total deductions
            ('FONT', (0, 7), (-1, 7), 'Helvetica-Bold', 9),
            ('BACKGROUND', (0, 7), (-1, 7), HexColor('#fff3cd')),
            ('ALIGN', (1, 7), (1, 7), 'RIGHT'),
            ('TOPPADDING', (0, 7), (-1, 7), 6),
            ('BOTTOMPADDING', (0, 7), (-1, 7), 6),

            # Net salary row
            ('FONT', (0, 8), (-1, 8), 'Helvetica-Bold', 12),
            ('BACKGROUND', (0, 8), (-1, 8), HexColor('#d4edda')),
            ('TEXTCOLOR', (0, 8), (-1, 8), dark_blue),
            ('ALIGN', (1, 8), (1, 8), 'RIGHT'),
            ('TOPPADDING', (0, 8), (-1, 8), 8),
            ('BOTTOMPADDING', (0, 8), (-1, 8), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        # Draw table
        table_width, table_height = table.wrap(0, 0)
        table.drawOn(c, margin, y - table_height)

        y -= table_height + 15*mm

        # ===== PAYMENT INFORMATION =====
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "PAYMENT INFORMATION:")

        y -= 6*mm

        c.setFont("Helvetica", 9)
        c.drawString(margin, y, "This amount will be transferred to your bank account by the pay date specified above.")

        # ===== CONFIDENTIALITY NOTICE =====
        y = 40*mm
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        notice = "CONFIDENTIAL: This document contains sensitive personal and financial information. Please keep it secure."
        notice_width = c.stringWidth(notice, "Helvetica", 8)
        c.drawString((width - notice_width) / 2, y, notice)

        # ===== FOOTER =====
        footer_y = 20*mm
        c.setFont("Helvetica", 8)

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
        """Generate HTML payslip (basic implementation)"""
        if output_path is None:
            filename = f"{data['payslip_number'].replace('/', '-')}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'payslips', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payslip {data['payslip_number']}</title>
        </head>
        <body>
            <h1>Payslip {data['payslip_number']}</h1>
            <p>Employee: {data['employee']['name']}</p>
            <p>Net Salary: {format_currency(data['net_salary'], self.language)}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
