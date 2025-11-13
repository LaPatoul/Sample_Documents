# ECM Document Generator - Quick Start Guide

## One-Command Setup

```bash
cd ecm-doc-generator
./setup.sh
```

That's it! The setup script will install everything you need.

## Starting the Application

### Terminal 1 - Backend Server
```bash
cd ecm-doc-generator/backend
source venv/bin/activate
python app.py
```

You should see:
```
ECM Document Generator - Backend Server
Database: ../database/ecm_docs.db
Storage: ../storage
Server starting on http://0.0.0.0:5000
```

### Terminal 2 - Frontend Server
```bash
cd ecm-doc-generator/frontend
npm start
```

Your browser will open automatically to `http://localhost:3000`

## First Steps

1. **Check the Dashboard**
   - Click "Dashboard" tab
   - You'll see stats (currently 0 documents)

2. **Generate Your First Document**
   - Click "Generate" tab
   - Leave default settings (Invoice, French, Modern, PDF)
   - Company is auto-set to Peters Engineering
   - Click "Generate" button
   - Click "Download" when ready

3. **Generate Bulk Documents**
   - Stay in "Generate" tab
   - Change "Quantity" to 10
   - Click "Generate"
   - Download the ZIP file with all 10 documents

4. **View History**
   - Click "History" tab
   - See all your generated documents
   - Download or preview any document

5. **Try Different Languages**
   - Click "DE" button in the top right to switch to German
   - Generate a document
   - Notice the UI and documents are in German

## What You Can Generate

### Document Types
- **Invoices**: Professional invoices with line items, tax calculations
- **Purchase Orders**: PO documents with vendor info and order details
- **Receipts**: Compact receipt format for payments

### Languages
- **French (FR)**: French language with EUR currency, French date format
- **German (DE)**: German language with EUR currency, German date format

### Template Styles
- **Modern**: Gradient header, contemporary design
- **Classic**: Traditional bordered layout

### Output Formats
- **PDF**: Ready-to-print PDF files
- **HTML**: Web-viewable HTML documents with preview

## Sample Use Cases

### Demo Preparation
Generate 50 sample invoices for a customer demo:
1. Set Document Type: Invoice
2. Set Quantity: 50
3. Click Generate
4. Download ZIP file
5. Extract and use for demo

### Multi-Language Testing
Test ECM system with German documents:
1. Switch UI to German (DE button)
2. Select Language: German
3. Generate documents
4. Test import into ECM

### Template Comparison
Compare Modern vs Classic styles:
1. Generate invoice with Modern style
2. Generate invoice with Classic style
3. Review both PDFs
4. Choose preferred style for production

## Quick Tips

- **Peters Engineering** is pre-loaded - great for consistent demos
- **Bulk generation** creates documents with varied dates and amounts
- **HTML preview** lets you see documents before downloading PDF
- **History tab** keeps track of everything you've generated
- Filter history by type or language to find specific documents

## Troubleshooting

### Backend won't start?
```bash
# Check Python version
python3 --version

# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Can't connect to backend?
Edit `frontend/src/components/DocumentForm.jsx` and similar files:
- Change `API_BASE` from `http://172.24.57.39:5000/api` to `http://localhost:5000/api`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code in `backend/generators/` to customize templates
- Add your own company presets to the database
- Customize colors and styling in `frontend/tailwind.config.js`

## Need Help?

Check the main README.md for:
- Detailed API documentation
- File structure explanation
- Development guidelines
- Common issues and solutions
