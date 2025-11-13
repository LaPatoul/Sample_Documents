"""
Employment Contract document generator
"""
import os
from datetime import datetime, timedelta
import random
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from utils.i18n import get_translation, format_date, format_currency
from utils.faker_data import get_generator


class ContractGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, company_data, employee_data=None, contract_number=None,
                 contract_date=None, start_date=None, contract_type='permanent',
                 position=None, salary=None, output_format='pdf', output_path=None):
        """
        Generate an employment contract document

        Args:
            company_data: Dict with company information
            employee_data: Dict with employee information (auto-generated if None)
            contract_number: Contract number (auto-generated if None)
            contract_date: Contract signing date (defaults to today)
            start_date: Employment start date
            contract_type: Type of contract (permanent, fixed_term, internship)
            position: Job position
            salary: Annual salary amount (auto-generated if None)
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if employee_data is None:
            employee_data = self._generate_employee_data()

        if contract_number is None:
            contract_number = self.data_gen.generate_document_number('contract')

        if contract_date is None:
            contract_date = datetime.now()

        if start_date is None:
            start_date = contract_date + timedelta(days=random.randint(7, 30))

        if position is None:
            position = random.choice([
                'Software Engineer', 'Project Manager', 'Sales Representative',
                'Marketing Manager', 'HR Manager', 'Accountant',
                'Product Designer', 'Business Analyst', 'Operations Manager'
            ])

        if salary is None:
            salary = random.randint(30000, 100000)

        # Generate contract terms
        terms = self._generate_contract_terms(contract_type, self.language)

        # Prepare document data
        doc_data = {
            'contract_number': contract_number,
            'contract_date': contract_date,
            'start_date': start_date,
            'contract_type': contract_type,
            'position': position,
            'salary': salary,
            'company': company_data,
            'employee': employee_data,
            'terms': terms,
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
            'address': self.data_gen.fake.address().replace('\n', ', '),
            'city': self.data_gen.fake.city(),
            'postal_code': self.data_gen.fake.postcode(),
            'country': self.data_gen.fake.country(),
            'email': self.data_gen.fake.email(),
            'phone': self.data_gen.fake.phone_number(),
            'date_of_birth': self.data_gen.fake.date_of_birth(minimum_age=22, maximum_age=60),
            'social_security_number': f"{random.randint(100000000, 999999999)}"
        }

    def _generate_contract_terms(self, contract_type, language):
        """Generate contract terms based on type"""
        terms = {
            'probation_period': '3 months' if contract_type == 'permanent' else '1 month',
            'notice_period': '2 months' if contract_type == 'permanent' else '1 month',
            'working_hours': '40 hours per week',
            'vacation_days': '25 days' if contract_type == 'permanent' else '2 days per month',
            'benefits': [
                'Health insurance',
                'Retirement plan',
                'Professional development budget',
                'Remote work options'
            ]
        }

        if contract_type == 'fixed_term':
            terms['contract_duration'] = f"{random.randint(6, 24)} months"
        elif contract_type == 'internship':
            terms['contract_duration'] = f"{random.randint(3, 6)} months"
            terms['benefits'] = ['Meal vouchers', 'Public transport allowance']

        return terms

    def _generate_pdf(self, data, output_path):
        """Generate professional PDF employment contract"""
        if output_path is None:
            filename = f"{data['contract_number'].replace('/', '-')}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'contracts', filename)

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

        # Company name (left) and CONTRACT title (right)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(dark_blue)
        c.drawString(margin, y, data['company']['name'])

        contract_title = get_translation('employment_contract', self.language).upper()
        title_width = c.stringWidth(contract_title, "Helvetica-Bold", 16)
        c.drawString(width - margin - title_width, y, contract_title)

        y -= 6*mm

        # Company details (left) and Contract number (right)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(margin, y, data['company']['address'])

        c.setFont("Helvetica", 10)
        contract_num = f"{get_translation('contract_number', self.language)}: {data['contract_number']}"
        num_width = c.stringWidth(contract_num, "Helvetica", 10)
        c.drawString(width - margin - num_width, y, contract_num)

        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"{data['company']['postal_code']} {data['company']['city']}, {data['company']['country']}")

        c.setFont("Helvetica", 10)
        date_str = format_date(data['contract_date'], self.language)
        date_text = f"{get_translation('date', self.language)}: {date_str}"
        date_width = c.stringWidth(date_text, "Helvetica", 10)
        c.drawString(width - margin - date_width, y, date_text)

        y -= 10*mm

        # Header separator line
        c.setStrokeColor(dark_blue)
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)

        y -= 10*mm

        # ===== CONTRACT PARTIES =====
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)
        c.drawString(margin, y, "BETWEEN:")

        y -= 7*mm

        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"The Employer: {data['company']['name']}")
        y -= 4*mm
        c.drawString(margin, y, f"Address: {data['company']['address']}, {data['company']['city']}")
        y -= 4*mm
        c.drawString(margin, y, f"VAT: {data['company'].get('tax_id', 'N/A')}")

        y -= 8*mm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "AND:")

        y -= 7*mm

        c.setFont("Helvetica", 9)
        c.drawString(margin, y, f"The Employee: {data['employee']['name']}")
        y -= 4*mm
        c.drawString(margin, y, f"Address: {data['employee']['address']}, {data['employee']['city']}")
        y -= 4*mm
        dob_str = format_date(data['employee']['date_of_birth'], self.language)
        c.drawString(margin, y, f"Date of Birth: {dob_str}")
        y -= 4*mm
        c.drawString(margin, y, f"SSN: {data['employee']['social_security_number']}")

        y -= 10*mm

        # ===== CONTRACT TERMS =====
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "CONTRACT TERMS:")

        y -= 8*mm

        c.setFont("Helvetica", 9)

        # Position
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "1. Position:")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 30*mm, y, data['position'])

        y -= 6*mm

        # Contract Type
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "2. Contract Type:")
        c.setFont("Helvetica", 9)
        contract_type_text = get_translation(data['contract_type'], self.language).capitalize()
        c.drawString(margin + 30*mm, y, contract_type_text)

        if 'contract_duration' in data['terms']:
            y -= 5*mm
            c.drawString(margin + 30*mm, y, f"Duration: {data['terms']['contract_duration']}")

        y -= 6*mm

        # Start Date
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "3. Start Date:")
        c.setFont("Helvetica", 9)
        start_str = format_date(data['start_date'], self.language)
        c.drawString(margin + 30*mm, y, start_str)

        y -= 6*mm

        # Salary
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "4. Compensation:")
        c.setFont("Helvetica", 9)
        annual_salary = format_currency(data['salary'], self.language)
        c.drawString(margin + 30*mm, y, f"Annual Salary: {annual_salary}")

        y -= 6*mm

        # Working Hours
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "5. Working Hours:")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 30*mm, y, data['terms']['working_hours'])

        y -= 6*mm

        # Probation Period
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "6. Probation Period:")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 30*mm, y, data['terms']['probation_period'])

        y -= 6*mm

        # Vacation
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "7. Vacation:")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 30*mm, y, data['terms']['vacation_days'])

        y -= 6*mm

        # Notice Period
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "8. Notice Period:")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 30*mm, y, data['terms']['notice_period'])

        y -= 6*mm

        # Benefits
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "9. Benefits:")
        y -= 5*mm
        c.setFont("Helvetica", 9)
        for benefit in data['terms']['benefits']:
            c.drawString(margin + 30*mm, y, f"• {benefit}")
            y -= 4*mm

        y -= 5*mm

        # ===== SIGNATURE SECTION =====
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "SIGNATURES:")

        y -= 15*mm

        # Employer signature
        c.setFont("Helvetica", 9)
        c.line(margin, y, margin + 70*mm, y)
        c.drawString(margin, y - 5*mm, "Employer Signature")
        c.drawString(margin, y - 9*mm, f"Date: ________________")

        # Employee signature
        c.line(width - margin - 70*mm, y, width - margin, y)
        c.drawString(width - margin - 70*mm, y - 5*mm, "Employee Signature")
        c.drawString(width - margin - 70*mm, y - 9*mm, f"Date: ________________")

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
        """Generate HTML employment contract (basic implementation)"""
        if output_path is None:
            filename = f"{data['contract_number'].replace('/', '-')}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'contracts', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Employment Contract {data['contract_number']}</title>
        </head>
        <body>
            <h1>Employment Contract {data['contract_number']}</h1>
            <p>Employee: {data['employee']['name']}</p>
            <p>Position: {data['position']}</p>
            <p>Salary: {format_currency(data['salary'], self.language)}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
