"""
ECM Document Generator - Flask Backend
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import zipfile
from datetime import datetime, timedelta
import random
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db, Company, Document, GenerationLog
from generators.invoice_generator import InvoiceGenerator
from generators.po_generator import PurchaseOrderGenerator
from generators.receipt_generator import ReceiptGenerator
from generators.order_generator import OrderGenerator
from generators.delivery_note_generator import DeliveryNoteGenerator
from generators.payslip_generator import PayslipGenerator
from generators.contract_generator import ContractGenerator
from generators.expense_report_generator import ExpenseReportGenerator
from generators.id_document_generator import IDDocumentGenerator
from utils.faker_data import get_generator
from utils.ubl_generator import InvoiceUBLGenerator, OrderUBLGenerator, DespatchAdviceUBLGenerator

app = Flask(__name__)
CORS(app)

# Initialize database
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'ecm_docs.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
session = init_db(db_path)

# Ensure storage directories exist
storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
for doc_type in ['invoices', 'purchase_orders', 'receipts', 'orders', 'delivery_notes',
                  'payslips', 'contracts', 'expense_reports', 'id_documents']:
    os.makedirs(os.path.join(storage_base, doc_type), exist_ok=True)


def get_peters_engineering():
    """Get Peters Engineering company data"""
    peters = session.query(Company).filter_by(is_preset=1).first()
    if not peters:
        # Create Peters Engineering if not exists
        peters = Company(
            name="Peters Engineering",
            address="789 Construction Ave",
            city="Coaster City",
            postal_code="CC 12345",
            country="France",
            phone="+33 1 23 45 67 89",
            email="contact@peters-engineering.com",
            tax_id="FR-87654321",
            website="www.peters-engineering.com",
            is_preset=1
        )
        session.add(peters)
        session.commit()
    return peters


def company_to_dict(company):
    """Convert Company model to dict"""
    return {
        'id': company.id,
        'name': company.name,
        'address': company.address,
        'city': company.city,
        'postal_code': company.postal_code,
        'country': company.country,
        'phone': company.phone,
        'email': company.email,
        'tax_id': company.tax_id,
        'website': company.website,
        'is_preset': company.is_preset
    }


def serialize_doc_data(doc_data):
    """Safely serialize document data to JSON, handling Company objects"""
    def convert_value(obj):
        if isinstance(obj, Company):
            return company_to_dict(obj)
        elif isinstance(obj, (datetime, timedelta)):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_value(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_value(item) for item in obj]
        else:
            return obj

    cleaned_data = convert_value(doc_data)
    return json.dumps(cleaned_data, default=str)


def generate_ubl_document(doc_type, doc_data, language):
    """Generate UBL XML document and save to file

    Args:
        doc_type: Document type (invoice, order, delivery_note)
        doc_data: Document data dictionary
        language: Language code

    Returns:
        Relative file path to the generated XML file
    """
    # Select appropriate UBL generator
    if doc_type == 'invoice':
        generator = InvoiceUBLGenerator()
        folder = 'invoices'
        doc_number = doc_data.get('invoice_number', 'INV-0001')
    elif doc_type == 'order':
        generator = OrderUBLGenerator()
        folder = 'orders'
        doc_number = doc_data.get('order_number', 'ORD-0001')
    elif doc_type == 'delivery_note':
        generator = DespatchAdviceUBLGenerator()
        folder = 'delivery_notes'
        doc_number = doc_data.get('delivery_note_number', 'DN-0001')
    else:
        raise ValueError(f"UBL format not supported for document type: {doc_type}")

    # Generate UBL XML
    xml_content = generator.generate(doc_data, language)

    # Create file paths
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{doc_number}_{timestamp}.xml"

    # Absolute path for writing file
    absolute_path = os.path.join(storage_base, folder, filename)

    # Relative path for database/API (from backend directory)
    relative_path = os.path.join('storage', folder, filename)

    # Save XML file
    with open(absolute_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    return relative_path


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'name': 'ECM Document Generator API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate',
            'bulk_generate': '/api/generate/bulk',
            'documents': '/api/documents',
            'companies': '/api/companies',
            'stats': '/api/stats'
        },
        'frontend': 'http://172.24.57.39:3000',
        'supported_languages': ['en-GB', 'en-US', 'fr', 'de', 'es', 'it']
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'ECM Document Generator API is running'})


@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    companies = session.query(Company).all()
    return jsonify([company_to_dict(c) for c in companies])


@app.route('/api/companies/peters', methods=['GET'])
def get_peters():
    """Get Peters Engineering company"""
    peters = get_peters_engineering()
    return jsonify(company_to_dict(peters))


@app.route('/api/companies/generate', methods=['POST'])
def generate_company():
    """Generate a random company"""
    data = request.json
    language = data.get('language', 'fr')

    data_gen = get_generator(language)
    company_data = data_gen.generate_company()

    company = Company(**company_data, is_preset=0)
    session.add(company)
    session.commit()

    return jsonify(company_to_dict(company))


@app.route('/api/generate/sample-data', methods=['POST'])
def generate_sample_data():
    """Generate sample data for a document without creating PDF"""
    try:
        data = request.json
        doc_type = data.get('document_type', 'invoice')
        language = data.get('language', 'en-GB')
        company_id = data.get('company_id')

        # Get company data
        if company_id:
            company = session.query(Company).get(company_id)
            if not company:
                return jsonify({'error': 'Company not found'}), 404
            company_data = company_to_dict(company)
        else:
            company_data = get_peters_engineering()

        # Generate sample data using data generator
        data_gen = get_generator(language)

        # Generate customer
        customer_data = data_gen.generate_customer()

        # Generate document-specific data
        sample_data = {
            'document_type': doc_type,
            'language': language,
            'company': company_data,
            'customer': customer_data
        }

        if doc_type in ['invoice', 'order', 'delivery_note']:
            # Generate items
            if doc_type == 'invoice':
                items = data_gen.generate_invoice_items(count=random.randint(3, 6))
            else:
                items = data_gen.generate_order_items(count=random.randint(3, 6))

            # Generate document number
            doc_number = data_gen.generate_document_number(doc_type)

            # Generate dates
            doc_date = datetime.now()
            due_date = doc_date + timedelta(days=30)

            # Calculate totals
            subtotal = sum(item['total'] for item in items)
            tax_rate = 0.20 if language.startswith('en') else 0.21
            tax_amount = round(subtotal * tax_rate, 2)
            total = round(subtotal + tax_amount, 2)

            sample_data.update({
                'document_number': doc_number,
                'document_date': doc_date.strftime('%Y-%m-%d'),
                'due_date': due_date.strftime('%Y-%m-%d'),
                'items': items,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
                'currency': 'GBP' if language == 'en-GB' else ('USD' if language == 'en-US' else 'EUR')
            })

            # Add delivery-specific fields
            if doc_type == 'delivery_note':
                sample_data['tracking_number'] = f"TRK-{random.randint(100000, 999999)}"
                sample_data['carrier'] = random.choice(['DHL', 'FedEx', 'UPS', 'DPD'])

            # Add order-specific fields
            if doc_type == 'order':
                sample_data['delivery_date'] = (doc_date + timedelta(days=7)).strftime('%Y-%m-%d')
                sample_data['status'] = 'confirmed'

        return jsonify({'success': True, 'data': sample_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_document():
    """Generate a single document"""
    try:
        data = request.json

        doc_type = data.get('document_type', 'invoice')
        language = data.get('language', 'fr')
        template_style = data.get('template_style', 'modern')
        output_format = data.get('output_format', 'pdf')
        company_id = data.get('company_id')
        custom_data = data.get('custom_data')  # Get custom editable data

        start_time = time.time()

        # Get company data
        if custom_data and 'company' in custom_data:
            # Use custom company data from editable form
            company_data = custom_data['company']
        elif company_id:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                return jsonify({'error': 'Company not found'}), 404
            company_data = company_to_dict(company)
        else:
            company_data = get_generator(language).generate_company()
            company_id = None

        # Determine color scheme: use random scheme for random companies, fixed for known companies
        color_scheme = None if company_id is None else 'blue_professional'

        # Generate document based on type
        if doc_type == 'invoice':
            # Generate document data first (without creating PDF if UBL)
            generator = InvoiceGenerator(language, template_style, color_scheme=color_scheme)

            if custom_data:
                # Use custom data from editable form
                doc_data = generator.generate(
                    company_data=company_data,
                    customer_data=custom_data.get('customer'),
                    items=custom_data.get('items'),
                    invoice_number=custom_data.get('document_number'),
                    invoice_date=datetime.strptime(custom_data['document_date'], '%Y-%m-%d') if custom_data.get('document_date') else None,
                    due_date=datetime.strptime(custom_data['due_date'], '%Y-%m-%d') if custom_data.get('due_date') else None,
                    output_format=output_format if output_format != 'ubl' else 'pdf'  # Generate data structure
                )
            else:
                # Generate random data
                doc_data = generator.generate(
                    company_data=company_data,
                    output_format=output_format if output_format != 'ubl' else 'pdf'  # Generate data structure
                )

            # If UBL format requested, generate UBL XML
            if output_format == 'ubl':
                ubl_file_path = generate_ubl_document(doc_type, doc_data, language)
                doc_data['file_path'] = ubl_file_path
        elif doc_type == 'purchase_order':
            generator = PurchaseOrderGenerator(language, template_style)
            doc_data = generator.generate(
                company_data=company_data,
                output_format=output_format
            )
        elif doc_type == 'receipt':
            generator = ReceiptGenerator(language, template_style)
            doc_data = generator.generate(
                company_data=company_data,
                output_format=output_format
            )
        elif doc_type == 'order':
            generator = OrderGenerator(language, template_style)

            if custom_data:
                # Use custom data from editable form
                doc_data = generator.generate(
                    company_data=company_data,
                    customer_data=custom_data.get('customer'),
                    items=custom_data.get('items'),
                    order_number=custom_data.get('document_number'),
                    order_date=datetime.strptime(custom_data['document_date'], '%Y-%m-%d') if custom_data.get('document_date') else None,
                    delivery_date=datetime.strptime(custom_data['delivery_date'], '%Y-%m-%d') if custom_data.get('delivery_date') else None,
                    status=custom_data.get('status', 'confirmed'),
                    output_format=output_format if output_format != 'ubl' else 'pdf'
                )
            else:
                # Generate random data
                doc_data = generator.generate(
                    company_data=company_data,
                    output_format=output_format if output_format != 'ubl' else 'pdf'
                )

            # If UBL format requested, generate UBL XML
            if output_format == 'ubl':
                ubl_file_path = generate_ubl_document(doc_type, doc_data, language)
                doc_data['file_path'] = ubl_file_path
        elif doc_type == 'delivery_note':
            generator = DeliveryNoteGenerator(language, template_style)

            if custom_data:
                # Use custom data from editable form
                doc_data = generator.generate(
                    company_data=company_data,
                    customer_data=custom_data.get('customer'),
                    items=custom_data.get('items'),
                    delivery_note_number=custom_data.get('document_number'),
                    order_number=custom_data.get('order_number'),
                    delivery_date=datetime.strptime(custom_data['document_date'], '%Y-%m-%d') if custom_data.get('document_date') else None,
                    tracking_number=custom_data.get('tracking_number'),
                    carrier=custom_data.get('carrier'),
                    output_format=output_format if output_format != 'ubl' else 'pdf'
                )
            else:
                # Generate random data
                doc_data = generator.generate(
                    company_data=company_data,
                    output_format=output_format if output_format != 'ubl' else 'pdf'
                )

            # If UBL format requested, generate UBL XML
            if output_format == 'ubl':
                ubl_file_path = generate_ubl_document(doc_type, doc_data, language)
                doc_data['file_path'] = ubl_file_path
        elif doc_type == 'payslip':
            generator = PayslipGenerator(language, template_style)
            doc_data = generator.generate(
                company_data=company_data,
                output_format=output_format
            )
        elif doc_type == 'contract':
            generator = ContractGenerator(language, template_style)
            doc_data = generator.generate(
                company_data=company_data,
                output_format=output_format
            )
        elif doc_type == 'expense_report':
            generator = ExpenseReportGenerator(language, template_style)
            doc_data = generator.generate(
                company_data=company_data,
                output_format=output_format
            )
        elif doc_type in ['id_card', 'carte_vitale', 'drivers_license']:
            generator = IDDocumentGenerator(language, template_style)
            doc_data = generator.generate(
                document_type=doc_type,
                output_format=output_format
            )
        else:
            return jsonify({'error': 'Invalid document type'}), 400

        # Extract document number based on type
        doc_number = (doc_data.get('invoice_number') or doc_data.get('po_number') or
                     doc_data.get('receipt_number') or doc_data.get('order_number') or
                     doc_data.get('delivery_note_number') or doc_data.get('payslip_number') or
                     doc_data.get('contract_number') or doc_data.get('report_number') or
                     doc_data.get('document_number'))

        # Save document metadata to database
        doc = Document(
            document_type=doc_type,
            document_number=doc_number,
            order_number=doc_data.get('order_number'),  # For linking related documents
            template_style=template_style,
            language=language,
            company_id=company_id,
            customer_name=doc_data.get('customer', {}).get('name') or doc_data.get('vendor', {}).get('name') or doc_data.get('employee', {}).get('name'),
            total_amount=doc_data.get('total'),
            currency='EUR',
            file_path=doc_data['file_path'],
            file_format=output_format,
            metadata_json=serialize_doc_data(doc_data)
        )
        session.add(doc)

        # Log generation
        duration = int(time.time() - start_time)
        log = GenerationLog(
            document_type=doc_type,
            quantity=1,
            language=language,
            template_style=template_style,
            status='success',
            duration_seconds=duration
        )
        session.add(log)
        session.commit()

        return jsonify({
            'success': True,
            'document': doc.to_dict(),
            'file_path': doc_data['file_path']
        })

    except Exception as e:
        # Log error
        log = GenerationLog(
            document_type=data.get('document_type', 'unknown'),
            quantity=1,
            language=data.get('language', 'fr'),
            template_style=data.get('template_style', 'modern'),
            status='failed',
            error_message=str(e)
        )
        session.add(log)
        session.commit()

        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/bulk', methods=['POST'])
def generate_bulk():
    """Generate multiple documents"""
    try:
        data = request.json

        doc_type = data.get('document_type', 'invoice')
        language = data.get('language', 'fr')
        template_style = data.get('template_style', 'modern')
        output_format = data.get('output_format', 'pdf')
        quantity = data.get('quantity', 10)
        company_id = data.get('company_id')
        date_range_start = data.get('date_range_start')
        date_range_end = data.get('date_range_end')

        if quantity > 100:
            return jsonify({'error': 'Maximum 100 documents per bulk generation'}), 400

        start_time = time.time()

        # Get company data
        if company_id:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                return jsonify({'error': 'Company not found'}), 404
            company_data = company_to_dict(company)
        else:
            company_data = None

        # Parse date range
        if date_range_start:
            date_start = datetime.fromisoformat(date_range_start.replace('Z', '+00:00'))
        else:
            date_start = datetime.now() - timedelta(days=90)

        if date_range_end:
            date_end = datetime.fromisoformat(date_range_end.replace('Z', '+00:00'))
        else:
            date_end = datetime.now()

        generated_files = []
        data_gen = get_generator(language)

        # Generate documents
        for i in range(quantity):
            # Use company_data or generate new one for each document
            if company_data is None:
                current_company_data = data_gen.generate_company()
            else:
                current_company_data = company_data

            # Random date within range
            doc_date = data_gen.generate_date_range(date_start, date_end)

            # Generate document based on type
            if doc_type == 'invoice':
                generator = InvoiceGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    invoice_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'purchase_order':
                generator = PurchaseOrderGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    order_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'receipt':
                generator = ReceiptGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    receipt_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'order':
                generator = OrderGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    order_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'delivery_note':
                generator = DeliveryNoteGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    delivery_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'payslip':
                generator = PayslipGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    pay_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'contract':
                generator = ContractGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    contract_date=doc_date,
                    output_format=output_format
                )
            elif doc_type == 'expense_report':
                generator = ExpenseReportGenerator(language, template_style)
                doc_data = generator.generate(
                    company_data=current_company_data,
                    report_date=doc_date,
                    output_format=output_format
                )
            elif doc_type in ['id_card', 'carte_vitale', 'drivers_license']:
                generator = IDDocumentGenerator(language, template_style)
                doc_data = generator.generate(
                    document_type=doc_type,
                    issue_date=doc_date,
                    output_format=output_format
                )

            generated_files.append(doc_data['file_path'])

            # Extract document number
            doc_number = (doc_data.get('invoice_number') or doc_data.get('po_number') or
                         doc_data.get('receipt_number') or doc_data.get('order_number') or
                         doc_data.get('delivery_note_number') or doc_data.get('payslip_number') or
                         doc_data.get('contract_number') or doc_data.get('report_number') or
                         doc_data.get('document_number'))

            # Save document metadata
            doc = Document(
                document_type=doc_type,
                document_number=doc_number,
                order_number=doc_data.get('order_number'),
                template_style=template_style,
                language=language,
                company_id=company_id,
                customer_name=doc_data.get('customer', {}).get('name') or doc_data.get('vendor', {}).get('name') or doc_data.get('employee', {}).get('name'),
                total_amount=doc_data.get('total'),
                currency='EUR',
                file_path=doc_data['file_path'],
                file_format=output_format,
                metadata_json=serialize_doc_data(doc_data)
            )
            session.add(doc)

        # Create ZIP file
        zip_filename = f"bulk_{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(storage_base, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in generated_files:
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
                zipf.write(full_path, os.path.basename(file_path))

        # Log generation
        duration = int(time.time() - start_time)
        log = GenerationLog(
            document_type=doc_type,
            quantity=quantity,
            language=language,
            template_style=template_style,
            status='success',
            duration_seconds=duration
        )
        session.add(log)
        session.commit()

        return jsonify({
            'success': True,
            'quantity': quantity,
            'zip_file': zip_filename,
            'files': generated_files
        })

    except Exception as e:
        # Log error
        log = GenerationLog(
            document_type=data.get('document_type', 'unknown'),
            quantity=data.get('quantity', 0),
            language=data.get('language', 'fr'),
            template_style=data.get('template_style', 'modern'),
            status='failed',
            error_message=str(e)
        )
        session.add(log)
        session.commit()

        return jsonify({'error': str(e)}), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get document history"""
    limit = request.args.get('limit', 50, type=int)
    doc_type = request.args.get('type')
    language = request.args.get('language')

    query = session.query(Document).order_by(Document.created_at.desc())

    if doc_type:
        query = query.filter_by(document_type=doc_type)
    if language:
        query = query.filter_by(language=language)

    documents = query.limit(limit).all()

    return jsonify([doc.to_dict() for doc in documents])


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get specific document"""
    doc = session.query(Document).filter_by(id=doc_id).first()
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify(doc.to_dict())


@app.route('/api/download/<path:file_path>', methods=['GET'])
def download_file(file_path):
    """Download a generated file"""
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(base_dir, file_path)

        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(full_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<path:file_path>', methods=['GET'])
def preview_file(file_path):
    """Preview a generated HTML file"""
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(base_dir, file_path)

        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404

        if file_path.endswith('.html'):
            return send_file(full_path)
        else:
            return jsonify({'error': 'Only HTML files can be previewed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get generation logs"""
    limit = request.args.get('limit', 50, type=int)
    logs = session.query(GenerationLog).order_by(GenerationLog.created_at.desc()).limit(limit).all()

    return jsonify([log.to_dict() for log in logs])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get generation statistics"""
    total_docs = session.query(Document).count()
    total_invoices = session.query(Document).filter_by(document_type='invoice').count()
    total_pos = session.query(Document).filter_by(document_type='purchase_order').count()
    total_receipts = session.query(Document).filter_by(document_type='receipt').count()
    total_orders = session.query(Document).filter_by(document_type='order').count()
    total_delivery_notes = session.query(Document).filter_by(document_type='delivery_note').count()
    total_payslips = session.query(Document).filter_by(document_type='payslip').count()
    total_contracts = session.query(Document).filter_by(document_type='contract').count()
    total_expense_reports = session.query(Document).filter_by(document_type='expense_report').count()
    total_id_docs = (session.query(Document).filter_by(document_type='id_card').count() +
                     session.query(Document).filter_by(document_type='carte_vitale').count() +
                     session.query(Document).filter_by(document_type='drivers_license').count())

    recent_logs = session.query(GenerationLog).order_by(GenerationLog.created_at.desc()).limit(10).all()

    return jsonify({
        'total_documents': total_docs,
        'by_type': {
            'invoices': total_invoices,
            'purchase_orders': total_pos,
            'receipts': total_receipts,
            'orders': total_orders,
            'delivery_notes': total_delivery_notes,
            'payslips': total_payslips,
            'contracts': total_contracts,
            'expense_reports': total_expense_reports,
            'id_documents': total_id_docs
        },
        'recent_activity': [log.to_dict() for log in recent_logs]
    })


if __name__ == '__main__':
    # Initialize Peters Engineering on startup
    get_peters_engineering()

    print("=" * 60)
    print("ECM Document Generator - Backend Server")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"Storage: {storage_base}")
    print("Server starting on http://0.0.0.0:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
