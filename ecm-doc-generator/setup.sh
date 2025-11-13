#!/bin/bash

set -e

echo "======================================"
echo "ECM Document Generator - Setup Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        echo -e "${YELLOW}Warning: This script is designed for Ubuntu. You may encounter issues on $ID.${NC}"
    fi
fi

echo -e "${BLUE}Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm

echo ""
echo -e "${BLUE}Step 2: Setting up Python virtual environment...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate

echo ""
echo -e "${BLUE}Step 3: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${BLUE}Step 4: Initializing database...${NC}"
cd ..
mkdir -p database storage/{invoices,purchase_orders,receipts}

# Initialize database by importing models
python3 -c "
import sys
sys.path.insert(0, 'backend')
from models import init_db, Company
session = init_db('database/ecm_docs.db')

# Create Peters Engineering preset company
peters = Company(
    name='Peters Engineering',
    address='789 Construction Ave',
    city='Coaster City',
    postal_code='CC 12345',
    country='France',
    phone='+33 1 23 45 67 89',
    email='contact@peters-engineering.com',
    tax_id='FR-87654321',
    website='www.peters-engineering.com',
    is_preset=1
)
session.add(peters)
session.commit()
print('Database initialized successfully!')
print('Peters Engineering company created.')
"

deactivate

echo ""
echo -e "${BLUE}Step 5: Setting up React frontend...${NC}"
cd frontend

# Install npm dependencies
npm install

echo ""
echo -e "${GREEN}======================================"
echo "Setup completed successfully!"
echo "======================================${NC}"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "The application will be available at:"
echo "   Backend API: http://172.24.57.39:5000"
echo "   Frontend UI: http://localhost:3000"
echo ""
echo -e "${GREEN}Happy document generating!${NC}"
