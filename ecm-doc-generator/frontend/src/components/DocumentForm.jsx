import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { API_BASE } from '../config/api';

function DocumentForm({ onGenerated }) {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState({
    document_type: 'invoice',
    language: i18n.language || 'en-GB',
    output_format: 'pdf',
    company_id: null
  });
  const [companies, setCompanies] = useState([]);
  const [sampleData, setSampleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  // Sync form language with header language switcher
  useEffect(() => {
    setFormData(prev => ({ ...prev, language: i18n.language }));
    // Reset sample data when language changes
    setSampleData(null);
  }, [i18n.language]);

  const loadCompanies = async () => {
    try {
      const response = await axios.get(`${API_BASE}/companies`);
      setCompanies(response.data);

      // Auto-select Peters Engineering if available
      const peters = response.data.find(c => c.is_preset === 1);
      if (peters) {
        setFormData(prev => ({ ...prev, company_id: peters.id }));
      }
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'company_id' ? parseInt(value) : value
    }));
    // Reset sample data when document type changes
    if (name === 'document_type') {
      setSampleData(null);
    }
  };

  const handleGenerateSample = async () => {
    // Only allow for invoice, order, delivery_note
    if (!['invoice', 'order', 'delivery_note'].includes(formData.document_type)) {
      setMessage({
        type: 'error',
        text: 'Editable form only available for Invoice, Order, and Delivery Note'
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post(`${API_BASE}/generate/sample-data`, {
        document_type: formData.document_type,
        language: formData.language,
        company_id: formData.company_id
      });

      if (response.data.success) {
        setSampleData(response.data.data);
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSampleDataChange = (field, value) => {
    setSampleData(prev => ({ ...prev, [field]: value }));
  };

  const handleItemChange = (index, field, value) => {
    setSampleData(prev => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: field === 'quantity' || field === 'unit_price' ? parseFloat(value) || 0 : value };

      // Recalculate item total
      newItems[index].total = newItems[index].quantity * newItems[index].unit_price;

      // Recalculate document totals
      const subtotal = newItems.reduce((sum, item) => sum + item.total, 0);
      const tax_amount = subtotal * prev.tax_rate;
      const total = subtotal + tax_amount;

      return {
        ...prev,
        items: newItems,
        subtotal: Math.round(subtotal * 100) / 100,
        tax_amount: Math.round(tax_amount * 100) / 100,
        total: Math.round(total * 100) / 100
      };
    });
  };

  const handleAddItem = () => {
    setSampleData(prev => ({
      ...prev,
      items: [...prev.items, { description: '', quantity: 1, unit: 'unit', unit_price: 0, total: 0 }]
    }));
  };

  const handleRemoveItem = (index) => {
    if (sampleData.items.length <= 1) return; // Keep at least one item

    setSampleData(prev => {
      const newItems = prev.items.filter((_, i) => i !== index);
      const subtotal = newItems.reduce((sum, item) => sum + item.total, 0);
      const tax_amount = subtotal * prev.tax_rate;
      const total = subtotal + tax_amount;

      return {
        ...prev,
        items: newItems,
        subtotal: Math.round(subtotal * 100) / 100,
        tax_amount: Math.round(tax_amount * 100) / 100,
        total: Math.round(total * 100) / 100
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post(`${API_BASE}/generate`, {
        ...formData,
        template_style: 'modern', // Always use modern
        custom_data: sampleData // Send the edited data
      });

      if (response.data.success) {
        setMessage({
          type: 'success',
          text: t('document_generated'),
          filePath: response.data.file_path
        });

        if (onGenerated) {
          onGenerated(response.data);
        }

        // Reset sample data after successful generation
        setSampleData(null);
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (filePath) => {
    window.open(`${API_BASE}/download/${filePath}`, '_blank');
  };

  const showEditableForm = sampleData && ['invoice', 'order', 'delivery_note'].includes(formData.document_type);

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">{t('generate')} {t('documents')}</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Document Type */}
          <div>
            <label className="label">{t('document_type')}</label>
            <select
              name="document_type"
              value={formData.document_type}
              onChange={handleChange}
              className="select-field"
              disabled={showEditableForm}
            >
              <option value="invoice">{t('invoice')}</option>
              <option value="purchase_order">{t('purchase_order')}</option>
              <option value="receipt">{t('receipt')}</option>
              <option value="order">{t('order')}</option>
              <option value="delivery_note">{t('delivery_note')}</option>
              <option value="payslip">{t('payslip')}</option>
              <option value="contract">{t('contract')}</option>
              <option value="expense_report">{t('expense_report')}</option>
              <option value="id_card">{t('id_card')}</option>
              <option value="carte_vitale">{t('carte_vitale')}</option>
              <option value="drivers_license">{t('drivers_license')}</option>
            </select>
          </div>

          {/* Company */}
          <div>
            <label className="label">{t('company')}</label>
            <select
              name="company_id"
              value={formData.company_id || ''}
              onChange={handleChange}
              className="select-field"
              disabled={showEditableForm}
            >
              <option value="">{t('generate_random')}</option>
              {companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name} {company.is_preset ? '(Peters Engineering)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Output Format */}
          <div>
            <label className="label">{t('output_format')}</label>
            <select
              name="output_format"
              value={formData.output_format}
              onChange={handleChange}
              className="select-field"
              disabled={showEditableForm}
            >
              <option value="pdf">{t('format_pdf')}</option>
              <option value="html">{t('format_html')}</option>
              {['invoice', 'order', 'delivery_note'].includes(formData.document_type) && (
                <option value="ubl">{t('format_ubl')}</option>
              )}
            </select>
          </div>
        </div>

        {/* Generate Sample Data Button */}
        {!showEditableForm && ['invoice', 'order', 'delivery_note'].includes(formData.document_type) && (
          <div className="flex justify-center">
            <button
              type="button"
              onClick={handleGenerateSample}
              disabled={loading}
              className="btn-primary px-8"
            >
              {loading ? t('generating') : '🎲 Generate Sample Data'}
            </button>
          </div>
        )}

        {/* Quick Generate for Non-Editable Documents */}
        {!showEditableForm && !['invoice', 'order', 'delivery_note'].includes(formData.document_type) && (
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary px-8"
            >
              {loading ? t('generating') : t('generate_button')}
            </button>
          </div>
        )}

        {/* Editable Form Fields */}
        {showEditableForm && (
          <div className="space-y-6 border-t pt-6">
            {/* Company Information */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-4">Company Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Company Name</label>
                  <input
                    type="text"
                    value={sampleData.company.name}
                    onChange={(e) => handleSampleDataChange('company', { ...sampleData.company, name: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Email</label>
                  <input
                    type="email"
                    value={sampleData.company.email}
                    onChange={(e) => handleSampleDataChange('company', { ...sampleData.company, email: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Address</label>
                  <input
                    type="text"
                    value={sampleData.company.address}
                    onChange={(e) => handleSampleDataChange('company', { ...sampleData.company, address: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="text"
                    value={sampleData.company.phone}
                    onChange={(e) => handleSampleDataChange('company', { ...sampleData.company, phone: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Customer Information */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-4">Customer Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Customer Name</label>
                  <input
                    type="text"
                    value={sampleData.customer.name}
                    onChange={(e) => handleSampleDataChange('customer', { ...sampleData.customer, name: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Email</label>
                  <input
                    type="email"
                    value={sampleData.customer.email}
                    onChange={(e) => handleSampleDataChange('customer', { ...sampleData.customer, email: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="label">Address</label>
                  <input
                    type="text"
                    value={sampleData.customer.address}
                    onChange={(e) => handleSampleDataChange('customer', { ...sampleData.customer, address: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Document Details */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-4">Document Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label">Document Number</label>
                  <input
                    type="text"
                    value={sampleData.document_number}
                    onChange={(e) => handleSampleDataChange('document_number', e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Document Date</label>
                  <input
                    type="date"
                    value={sampleData.document_date}
                    onChange={(e) => handleSampleDataChange('document_date', e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="label">Due Date</label>
                  <input
                    type="date"
                    value={sampleData.due_date}
                    onChange={(e) => handleSampleDataChange('due_date', e.target.value)}
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Line Items */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-4">Line Items</h3>
              <div className="space-y-3">
                {sampleData.items.map((item, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 items-end">
                    <div className="col-span-5">
                      <label className="label text-xs">Description</label>
                      <input
                        type="text"
                        value={item.description}
                        onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                        className="input-field text-sm"
                        placeholder="Item description"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="label text-xs">Quantity</label>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                        className="input-field text-sm"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="label text-xs">Unit Price</label>
                      <input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                        className="input-field text-sm"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="label text-xs">Total</label>
                      <input
                        type="number"
                        value={item.total}
                        className="input-field text-sm bg-gray-100"
                        readOnly
                      />
                    </div>
                    <div className="col-span-1">
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(index)}
                        className="btn-secondary text-sm h-10 w-full"
                        disabled={sampleData.items.length <= 1}
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddItem}
                  className="btn-secondary text-sm"
                >
                  + Add Item
                </button>
              </div>
            </div>

            {/* Totals */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-lg mb-4">Totals</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label">Subtotal</label>
                  <input
                    type="number"
                    value={sampleData.subtotal}
                    className="input-field bg-gray-100"
                    readOnly
                  />
                </div>
                <div>
                  <label className="label">Tax ({(sampleData.tax_rate * 100).toFixed(0)}%)</label>
                  <input
                    type="number"
                    value={sampleData.tax_amount}
                    className="input-field bg-gray-100"
                    readOnly
                  />
                </div>
                <div>
                  <label className="label">Total</label>
                  <input
                    type="number"
                    value={sampleData.total}
                    className="input-field bg-gray-100 font-bold"
                    readOnly
                  />
                </div>
              </div>
            </div>

            {/* Generate PDF Button */}
            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={() => setSampleData(null)}
                className="btn-secondary"
              >
                ← Back to Setup
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary px-8"
              >
                {loading ? t('generating') : '📄 Generate PDF'}
              </button>
            </div>
          </div>
        )}

        {/* Message */}
        {message && (
          <div className={`p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex justify-between items-start">
              <div>
                <h3 className={`font-semibold ${
                  message.type === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {message.type === 'success' ? t('success') : t('error')}
                </h3>
                <p className={message.type === 'success' ? 'text-green-700' : 'text-red-700'}>
                  {message.text}
                </p>
              </div>
              {message.type === 'success' && message.filePath && (
                <button
                  onClick={() => handleDownload(message.filePath)}
                  className="btn-primary text-sm"
                >
                  {t('download')}
                </button>
              )}
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

export default DocumentForm;
