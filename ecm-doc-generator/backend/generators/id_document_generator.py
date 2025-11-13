"""
Personal ID Document generator (ID Card, Carte Vitale, Driver's License)
"""
import os
from datetime import datetime, timedelta
import random
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, grey, white
from reportlab.lib import colors
from utils.i18n import get_translation, format_date
from utils.faker_data import get_generator


class IDDocumentGenerator:
    def __init__(self, language='en-GB', template_style='modern'):
        self.language = language
        self.template_style = template_style
        self.data_gen = get_generator(language)

    def generate(self, document_type='id_card', person_data=None,
                 document_number=None, issue_date=None, expiry_date=None,
                 output_format='pdf', output_path=None):
        """
        Generate a personal ID document

        Args:
            document_type: Type of ID (id_card, carte_vitale, drivers_license)
            person_data: Dict with person information (auto-generated if None)
            document_number: Document number (auto-generated if None)
            issue_date: Issue date
            expiry_date: Expiry date
            output_format: 'pdf' or 'html'
            output_path: Full path to output file

        Returns:
            Dict with document data and file path
        """
        # Generate missing data
        if person_data is None:
            person_data = self._generate_person_data()

        if document_number is None:
            document_number = self._generate_document_number(document_type)

        if issue_date is None:
            issue_date = datetime.now() - timedelta(days=random.randint(365, 1825))

        if expiry_date is None:
            # ID cards and licenses typically valid for 10-15 years
            years_valid = 10 if document_type in ['id_card', 'drivers_license'] else 100
            expiry_date = issue_date + timedelta(days=365 * years_valid)

        # Prepare document data
        doc_data = {
            'document_type': document_type,
            'document_number': document_number,
            'issue_date': issue_date,
            'expiry_date': expiry_date,
            'person': person_data,
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

    def _generate_person_data(self):
        """Generate random person data"""
        return {
            'first_name': self.data_gen.fake.first_name(),
            'last_name': self.data_gen.fake.last_name(),
            'date_of_birth': self.data_gen.fake.date_of_birth(minimum_age=18, maximum_age=80),
            'place_of_birth': self.data_gen.fake.city(),
            'nationality': self.data_gen.fake.country(),
            'sex': random.choice(['M', 'F']),
            'address': self.data_gen.fake.address().replace('\n', ', '),
            'city': self.data_gen.fake.city(),
            'postal_code': self.data_gen.fake.postcode(),
            'height': f"{random.randint(150, 195)} cm",
            'eye_color': random.choice(['Brown', 'Blue', 'Green', 'Hazel', 'Grey']),
            'blood_type': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
        }

    def _generate_document_number(self, doc_type):
        """Generate document number based on type"""
        if doc_type == 'id_card':
            return f"ID{random.randint(100000000, 999999999)}"
        elif doc_type == 'carte_vitale':
            # French social security number format: 1 or 2 + YY + MM + dept + commune + order
            sex_code = random.choice([1, 2])
            year = str(random.randint(40, 99)).zfill(2)
            month = str(random.randint(1, 12)).zfill(2)
            dept = str(random.randint(1, 95)).zfill(2)
            commune = str(random.randint(1, 999)).zfill(3)
            order = str(random.randint(1, 999)).zfill(3)
            key = str(random.randint(1, 97)).zfill(2)
            return f"{sex_code}{year}{month}{dept}{commune}{order}{key}"
        elif doc_type == 'drivers_license':
            return f"DL{random.randint(10000000, 99999999)}"

    def _generate_pdf(self, data, output_path):
        """Generate professional PDF ID document"""
        if output_path is None:
            filename = f"{data['document_type']}_{data['document_number']}.pdf"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'id_documents', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create canvas with A4 page (will place ID card in center)
        c = pdf_canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # ID card dimensions (standard credit card size: 85.6mm x 53.98mm)
        if data['document_type'] == 'carte_vitale':
            card_width = 85.6*mm
            card_height = 53.98*mm
        elif data['document_type'] == 'drivers_license':
            card_width = 85.6*mm
            card_height = 53.98*mm
        else:  # id_card
            card_width = 85.6*mm
            card_height = 53.98*mm

        # Center the card on the page
        card_x = (width - card_width) / 2
        card_y = (height - card_height) / 2

        # Generate specific document type
        if data['document_type'] == 'id_card':
            self._draw_id_card(c, card_x, card_y, card_width, card_height, data)
        elif data['document_type'] == 'carte_vitale':
            self._draw_carte_vitale(c, card_x, card_y, card_width, card_height, data)
        elif data['document_type'] == 'drivers_license':
            self._draw_drivers_license(c, card_x, card_y, card_width, card_height, data)

        # Save PDF
        c.save()

        # Return relative path for API
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)

    def _draw_id_card(self, c, x, y, w, h, data):
        """Draw national ID card"""
        # Card background
        c.setFillColor(HexColor('#e8f4f8'))
        c.rect(x, y, w, h, fill=1, stroke=0)

        # Border
        c.setStrokeColor(HexColor('#2c5282'))
        c.setLineWidth(1)
        c.rect(x, y, w, h, fill=0, stroke=1)

        # Header bar
        c.setFillColor(HexColor('#2c5282'))
        c.rect(x, y + h - 12*mm, w, 12*mm, fill=1, stroke=0)

        # Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        title = "NATIONAL IDENTITY CARD"
        c.drawString(x + 5*mm, y + h - 8*mm, title)

        # SAMPLE watermark
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(1, 0, 0, alpha=0.3)
        sample_x = x + w/2 - 20*mm
        sample_y = y + h/2 - 3*mm
        c.drawString(sample_x, sample_y, "SAMPLE")

        # Photo placeholder
        c.setFillColor(colors.lightgrey)
        photo_x = x + 5*mm
        photo_y = y + 8*mm
        photo_w = 25*mm
        photo_h = 30*mm
        c.rect(photo_x, photo_y, photo_w, photo_h, fill=1, stroke=1)

        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 8)
        c.drawString(photo_x + 4*mm, photo_y + photo_h/2, "PHOTO")

        # Personal information
        info_x = x + 35*mm
        info_y = y + h - 18*mm

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 7)

        fields = [
            (f"Last Name:", data['person']['last_name'].upper()),
            (f"First Name:", data['person']['first_name']),
            (f"Date of Birth:", format_date(data['person']['date_of_birth'], self.language)),
            (f"Place of Birth:", data['person']['place_of_birth']),
            (f"Nationality:", data['person']['nationality']),
            (f"Sex:", data['person']['sex']),
            (f"ID Number:", data['document_number']),
            (f"Issue Date:", format_date(data['issue_date'], self.language)),
            (f"Expiry Date:", format_date(data['expiry_date'], self.language))
        ]

        for label, value in fields:
            c.setFont("Helvetica-Bold", 7)
            c.drawString(info_x, info_y, label)
            c.setFont("Helvetica", 7)
            c.drawString(info_x + 18*mm, info_y, value)
            info_y -= 4*mm

        # Barcode placeholder at bottom
        c.setFillColor(colors.black)
        barcode_y = y + 3*mm
        for i in range(40):
            bar_width = random.choice([0.5*mm, 1*mm, 1.5*mm])
            c.rect(x + 5*mm + i*2*mm, barcode_y, bar_width, 4*mm, fill=1, stroke=0)

    def _draw_carte_vitale(self, c, x, y, w, h, data):
        """Draw French Carte Vitale (health insurance card)"""
        # Card background (green)
        c.setFillColor(HexColor('#c8e6c9'))
        c.rect(x, y, w, h, fill=1, stroke=0)

        # Border
        c.setStrokeColor(HexColor('#2e7d32'))
        c.setLineWidth(1)
        c.rect(x, y, w, h, fill=0, stroke=1)

        # Header bar
        c.setFillColor(HexColor('#2e7d32'))
        c.rect(x, y + h - 10*mm, w, 10*mm, fill=1, stroke=0)

        # Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 5*mm, y + h - 7*mm, "CARTE VITALE")

        # SAMPLE watermark
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(1, 0, 0, alpha=0.3)
        c.drawString(x + w/2 - 20*mm, y + h/2 - 3*mm, "SAMPLE")

        # Personal information
        info_x = x + 5*mm
        info_y = y + h - 15*mm

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(info_x, info_y, f"{data['person']['last_name'].upper()} {data['person']['first_name']}")

        info_y -= 5*mm
        c.setFont("Helvetica", 7)
        c.drawString(info_x, info_y, f"Social Security Number:")
        info_y -= 4*mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(info_x, info_y, data['document_number'])

        info_y -= 6*mm
        c.setFont("Helvetica", 7)
        dob_str = format_date(data['person']['date_of_birth'], self.language)
        c.drawString(info_x, info_y, f"Date of Birth: {dob_str}")

        info_y -= 4*mm
        c.drawString(info_x, info_y, f"Place of Birth: {data['person']['place_of_birth']}")

        # Chip placeholder
        c.setFillColor(HexColor('#ffd700'))
        chip_x = x + w - 15*mm
        chip_y = y + h - 25*mm
        c.rect(chip_x, chip_y, 10*mm, 8*mm, fill=1, stroke=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 6)
        c.drawString(chip_x + 2*mm, chip_y + 3*mm, "CHIP")

        # Issue date at bottom
        c.setFont("Helvetica", 6)
        issue_str = format_date(data['issue_date'], self.language)
        c.drawString(x + 5*mm, y + 3*mm, f"Issued: {issue_str}")

    def _draw_drivers_license(self, c, x, y, w, h, data):
        """Draw driver's license"""
        # Card background (light pink/EU standard)
        c.setFillColor(HexColor('#fff0f5'))
        c.rect(x, y, w, h, fill=1, stroke=0)

        # Border
        c.setStrokeColor(HexColor('#8b4789'))
        c.setLineWidth(1)
        c.rect(x, y, w, h, fill=0, stroke=1)

        # EU flag (simplified)
        c.setFillColor(HexColor('#003399'))
        c.rect(x, y + h - 8*mm, 12*mm, 8*mm, fill=1, stroke=0)

        # Stars representation
        c.setFillColor(HexColor('#ffcc00'))
        for i in range(12):
            angle = i * 30
            star_x = x + 6*mm
            star_y = y + h - 4*mm
            c.circle(star_x, star_y, 0.3*mm, fill=1)

        # Title
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 14*mm, y + h - 5*mm, "DRIVING LICENCE")

        # SAMPLE watermark
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(1, 0, 0, alpha=0.3)
        c.drawString(x + w/2 - 20*mm, y + h/2 - 3*mm, "SAMPLE")

        # Photo placeholder
        c.setFillColor(colors.lightgrey)
        photo_x = x + 5*mm
        photo_y = y + 8*mm
        photo_w = 22*mm
        photo_h = 28*mm
        c.rect(photo_x, photo_y, photo_w, photo_h, fill=1, stroke=1)

        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 8)
        c.drawString(photo_x + 3*mm, photo_y + photo_h/2, "PHOTO")

        # Personal information
        info_x = x + 30*mm
        info_y = y + h - 12*mm

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 7)

        fields = [
            ("1.", data['person']['last_name'].upper()),
            ("2.", data['person']['first_name']),
            ("3.", format_date(data['person']['date_of_birth'], self.language) + f" {data['person']['place_of_birth']}"),
            ("4a.", format_date(data['issue_date'], self.language)),
            ("4b.", format_date(data['expiry_date'], self.language)),
            ("5.", data['document_number']),
            ("7.", "___________"),  # Signature placeholder
            ("9.", "B, B1, BE")  # License categories
        ]

        for label, value in fields:
            c.setFont("Helvetica-Bold", 6)
            c.drawString(info_x, info_y, label)
            c.setFont("Helvetica", 6)
            c.drawString(info_x + 5*mm, info_y, value[:35])
            info_y -= 4*mm

    def _generate_html(self, data, output_path):
        """Generate HTML ID document (basic implementation)"""
        if output_path is None:
            filename = f"{data['document_type']}_{data['document_number']}.html"
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_path = os.path.join(project_root, 'storage', 'id_documents', filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Basic HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{data['document_type']} - {data['document_number']}</title>
        </head>
        <body>
            <h1>{data['document_type'].replace('_', ' ').title()}</h1>
            <p>Document Number: {data['document_number']}</p>
            <p>Name: {data['person']['first_name']} {data['person']['last_name']}</p>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.relpath(output_path, project_root)
