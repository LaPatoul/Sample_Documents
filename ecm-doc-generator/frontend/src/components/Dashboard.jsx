import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const API_BASE = 'http://5.49.237.223:45000/api';

function Dashboard() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        <p className="mt-4 text-gray-600">{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-primary-500 to-primary-700 text-white">
          <h3 className="text-lg font-semibold opacity-90">{t('total_documents')}</h3>
          <p className="text-4xl font-bold mt-2">{stats?.total_documents || 0}</p>
        </div>

        <div className="card bg-gradient-to-br from-blue-500 to-blue-700 text-white">
          <h3 className="text-lg font-semibold opacity-90">{t('invoices')}</h3>
          <p className="text-4xl font-bold mt-2">{stats?.by_type?.invoices || 0}</p>
        </div>

        <div className="card bg-gradient-to-br from-green-500 to-green-700 text-white">
          <h3 className="text-lg font-semibold opacity-90">{t('purchase_orders')}</h3>
          <p className="text-4xl font-bold mt-2">{stats?.by_type?.purchase_orders || 0}</p>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-700 text-white">
          <h3 className="text-lg font-semibold opacity-90">{t('receipts')}</h3>
          <p className="text-4xl font-bold mt-2">{stats?.by_type?.receipts || 0}</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-bold mb-4">{t('recent_activity')}</h3>
        {stats?.recent_activity?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('document_type')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('quantity')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('language')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('status')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('duration')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.recent_activity.map((log, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {t(log.document_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.language?.toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        log.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.duration_seconds} {t('seconds')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">{t('no_documents')}</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
