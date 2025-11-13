import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const API_BASE = 'http://5.49.237.223:45000/api';

function DocumentForm({ onGenerated }) {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState({
    document_type: 'invoice',
    language: i18n.language || 'en-GB',
    template_style: 'modern',
    output_format: 'pdf',
    quantity: 1,
    company_id: null
  });
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  // Sync form language with header language switcher
  useEffect(() => {
    setFormData(prev => ({ ...prev, language: i18n.language }));
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
      [name]: name === 'quantity' || name === 'company_id' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const isBulk = formData.quantity > 1;
      const endpoint = isBulk ? `${API_BASE}/generate/bulk` : `${API_BASE}/generate`;

      const response = await axios.post(endpoint, formData);

      if (response.data.success) {
        if (isBulk) {
          setMessage({
            type: 'success',
            text: `${response.data.quantity} ${t('documents_generated')}`,
            zipFile: response.data.zip_file
          });
        } else {
          setMessage({
            type: 'success',
            text: t('document_generated'),
            filePath: response.data.file_path
          });
        }

        if (onGenerated) {
          onGenerated(response.data);
        }
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

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">{t('generate')} {t('documents')}</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Document Type */}
          <div>
            <label className="label">{t('document_type')}</label>
            <select
              name="document_type"
              value={formData.document_type}
              onChange={handleChange}
              className="select-field"
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

          {/* Template Style */}
          <div>
            <label className="label">{t('template_style')}</label>
            <select
              name="template_style"
              value={formData.template_style}
              onChange={handleChange}
              className="select-field"
            >
              <option value="modern">{t('modern')}</option>
              <option value="classic">{t('classic')}</option>
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
            >
              <option value="pdf">PDF</option>
              <option value="html">HTML</option>
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
            >
              <option value="">{t('generate_random')}</option>
              {companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name} {company.is_preset ? '(Peters Engineering)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Quantity */}
          <div>
            <label className="label">{t('quantity')}</label>
            <input
              type="number"
              name="quantity"
              min="1"
              max="100"
              value={formData.quantity}
              onChange={handleChange}
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.quantity === 1 ? t('single_document') : t('bulk_generation')}
            </p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary px-8 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t('generating') : t('generate_button')}
          </button>
        </div>

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
              {message.type === 'success' && (
                <div className="space-x-2">
                  {message.filePath && (
                    <button
                      onClick={() => handleDownload(message.filePath)}
                      className="btn-primary text-sm"
                    >
                      {t('download')}
                    </button>
                  )}
                  {message.zipFile && (
                    <button
                      onClick={() => handleDownload(`storage/${message.zipFile}`)}
                      className="btn-primary text-sm"
                    >
                      {t('download_zip')}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

export default DocumentForm;
