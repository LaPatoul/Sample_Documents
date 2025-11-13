# ECM Document Generator

A web-based application for generating realistic sample documents (invoices, purchase orders, receipts) for ECM software demonstrations and testing.

## Overview

The ECM Document Generator is a self-hosted application that runs on Ubuntu VM and helps teams quickly generate professional-looking sample documents in multiple languages with realistic data.

### Features

- **Multiple Document Types**: Generate invoices, purchase orders, and receipts
- **Multi-Language Support**: French and German UI and document templates
- **Template Styles**: Modern and Classic design options
- **Bulk Generation**: Generate 1-100 documents at once
- **Realistic Data**: Uses Faker library to generate authentic-looking business data
- **Multiple Formats**: Export as PDF or HTML
- **Pre-configured Company**: Peters Engineering preset company data
- **History Tracking**: View and download previously generated documents
- **Statistics Dashboard**: Track generation activity and document counts

## Technology Stack

### Backend
- **Python 3** with Flask framework
- **SQLite** database with SQLAlchemy ORM
- **ReportLab** for PDF generation
- **python-docx** for Word documents
- **Faker** for synthetic data generation
- **Jinja2** for HTML templating

### Frontend
- **React 18** with modern hooks
- **Tailwind CSS** for styling
- **react-i18next** for internationalization
- **Axios** for API communication

## Installation

### Prerequisites

- Ubuntu 20.04 or later
- Python 3.8+
- Node.js 14+ and npm
- Internet connection (for initial setup only)

### Quick Setup

1. Clone or copy this project to your Ubuntu VM

2. Run the automated setup script:
```bash
cd ecm-doc-generator
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install system dependencies (Python, Node.js)
- Create Python virtual environment
- Install Python packages
- Initialize SQLite database
- Create Peters Engineering preset company
- Install npm packages for React frontend

### Manual Setup

If you prefer manual installation:

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
cd ..
mkdir -p database storage/{invoices,purchase_orders,receipts}
```

#### Frontend Setup
```bash
cd frontend
npm install
```

#### Database Initialization
```bash
# From project root, with backend venv activated
python3 backend/app.py
# This will auto-create the database and Peters Engineering company
# Stop with Ctrl+C after startup
```

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate
python app.py
```

The backend API will be available at: `http://172.24.57.39:5000`

### Start Frontend Development Server

In a separate terminal:
```bash
cd frontend
npm start
```

The React app will open automatically at: `http://localhost:3000`

### Production Build (Frontend)

To create an optimized production build:
```bash
cd frontend
npm run build
```

Then serve the `build` folder with a web server like nginx.

## Usage Guide

### Generating Documents

1. **Navigate to Generate Tab**
   - Select document type (Invoice, Purchase Order, or Receipt)
   - Choose language (French or German)
   - Select template style (Modern or Classic)
   - Pick output format (PDF or HTML)

2. **Company Selection**
   - Use Peters Engineering (preset)
   - Select an existing company
   - Generate random company (auto-generated)

3. **Single vs Bulk Generation**
   - **Single**: Set quantity to 1 for one document
   - **Bulk**: Set quantity 2-100 for multiple documents with varied data
   - Bulk documents are downloaded as a ZIP file

4. **Download**
   - Click Download button after generation
   - HTML documents can be previewed in browser
   - PDF documents download directly

### Viewing History

1. Navigate to the **History** tab
2. Filter by document type or language
3. View document details in the table
4. Download or preview any previously generated document

### Dashboard

View statistics:
- Total documents generated
- Breakdown by document type
- Recent generation activity
- Generation success/failure status

## Document Templates

### Invoice Template
- Company information header
- Customer billing details
- Invoice number, date, and due date
- Itemized line items with quantities and prices
- Subtotal, tax (TVA/MwSt), and total
- Professional gradient design (Modern) or bordered layout (Classic)
- Sample watermark overlay

### Purchase Order Template
- Company and vendor information
- PO number, order date, delivery date
- Order status (Pending, Approved, Received)
- Product line items with quantities
- Totals with tax calculations

### Receipt Template
- Compact design (80mm width)
- Company details
- Receipt number and date
- Item list with totals
- Payment method
- Thank you message

## Configuration

### Backend Configuration

Edit `backend/app.py` to modify:
- Server host/port (default: `0.0.0.0:5000`)
- Database path
- Storage directories

### Frontend Configuration

Edit `frontend/src/components/` files to change:
- API endpoint (`API_BASE` constant)
- UI text and labels
- Component styling

### Adding New Languages

1. Create translation file: `frontend/src/i18n/[lang].json`
2. Add to `frontend/src/i18n/config.js`
3. Add backend translations in `backend/utils/i18n.py`

## File Structure

```
ecm-doc-generator/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── document.py
│   │   └── generation_log.py
│   ├── generators/            # Document generators
│   │   ├── invoice_generator.py
│   │   ├── po_generator.py
│   │   └── receipt_generator.py
│   ├── utils/                 # Utilities
│   │   ├── faker_data.py
│   │   ├── pdf_generator.py
│   │   └── i18n.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DocumentForm.jsx
│   │   │   └── History.jsx
│   │   ├── i18n/              # Translations
│   │   │   ├── config.js
│   │   │   ├── fr.json
│   │   │   └── de.json
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── storage/                   # Generated documents
│   ├── invoices/
│   ├── purchase_orders/
│   └── receipts/
├── database/
│   └── ecm_docs.db           # SQLite database
├── setup.sh                   # Setup script
└── README.md
```

## API Endpoints

### Documents
- `GET /api/health` - Health check
- `POST /api/generate` - Generate single document
- `POST /api/generate/bulk` - Generate multiple documents
- `GET /api/documents` - List documents (with filters)
- `GET /api/documents/<id>` - Get document details
- `GET /api/download/<path>` - Download file
- `GET /api/preview/<path>` - Preview HTML file

### Companies
- `GET /api/companies` - List all companies
- `GET /api/companies/peters` - Get Peters Engineering
- `POST /api/companies/generate` - Generate random company

### Statistics
- `GET /api/stats` - Get generation statistics
- `GET /api/logs` - Get generation logs

## Troubleshooting

### Backend won't start
- Check Python version: `python3 --version` (should be 3.8+)
- Verify virtual environment is activated
- Check if port 5000 is available: `lsof -i :5000`
- Review error logs in terminal

### Frontend won't start
- Check Node.js version: `node --version` (should be 14+)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Database errors
- Delete and recreate: `rm database/ecm_docs.db` then restart backend
- Check file permissions on database directory

### PDF generation issues
- Ensure ReportLab is installed: `pip install reportlab`
- Check write permissions on `storage/` directories

### Network connectivity
- Backend: Ensure Flask is listening on `0.0.0.0` not `127.0.0.1`
- Frontend: Update `API_BASE` in components to match your VM IP
- Firewall: Allow ports 5000 (backend) and 3000 (frontend)

## Peters Engineering Data

The application comes pre-configured with Peters Engineering company:

- **Name**: Peters Engineering
- **Address**: 789 Construction Ave, Coaster City, CC 12345
- **Country**: France
- **Phone**: +33 1 23 45 67 89
- **Email**: contact@peters-engineering.com
- **Tax ID**: FR-87654321

You can select this company when generating documents to maintain consistency across samples.

## Development

### Adding New Document Types

1. Create generator class in `backend/generators/`
2. Implement HTML template in generator
3. Add document type to frontend forms
4. Update translations in i18n files

### Customizing Templates

Templates are embedded in generator classes:
- PDF: Modify ReportLab drawing code
- HTML: Edit HTML template strings in `_create_html_template()` methods

### Database Schema

**companies**: id, name, address, city, postal_code, country, phone, email, tax_id, website, is_preset

**documents**: id, document_type, document_number, template_style, language, company_id, customer_name, total_amount, currency, file_path, file_format, created_at, metadata_json

**generation_logs**: id, document_type, quantity, language, template_style, status, error_message, created_at, duration_seconds

## License

This is a sample/demo application for ECM software testing purposes.

## Support

For issues, questions, or contributions, please contact your development team.
