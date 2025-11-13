import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Dashboard from './components/Dashboard';
import DocumentForm from './components/DocumentForm';
import History from './components/History';
import './i18n/config';

function App() {
  const { t, i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState('generate');
  const [refreshKey, setRefreshKey] = useState(0);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  const handleDocumentGenerated = () => {
    // Trigger refresh of dashboard and history
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">{t('app_title')}</h1>
              <p className="text-primary-100 mt-1">{t('app_subtitle')}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => changeLanguage('en-GB')}
                className={`px-3 py-2 rounded-lg transition text-sm ${
                  i18n.language === 'en-GB'
                    ? 'bg-white text-primary-600 font-semibold'
                    : 'bg-primary-700 hover:bg-primary-600'
                }`}
              >
                🇬🇧 EN-GB
              </button>
              <button
                onClick={() => changeLanguage('en-US')}
                className={`px-3 py-2 rounded-lg transition text-sm ${
                  i18n.language === 'en-US'
                    ? 'bg-white text-primary-600 font-semibold'
                    : 'bg-primary-700 hover:bg-primary-600'
                }`}
              >
                🇺🇸 EN-US
              </button>
              <button
                onClick={() => changeLanguage('fr')}
                className={`px-3 py-2 rounded-lg transition text-sm ${
                  i18n.language === 'fr'
                    ? 'bg-white text-primary-600 font-semibold'
                    : 'bg-primary-700 hover:bg-primary-600'
                }`}
              >
                🇫🇷 FR
              </button>
              <button
                onClick={() => changeLanguage('de')}
                className={`px-3 py-2 rounded-lg transition text-sm ${
                  i18n.language === 'de'
                    ? 'bg-white text-primary-600 font-semibold'
                    : 'bg-primary-700 hover:bg-primary-600'
                }`}
              >
                🇩🇪 DE
              </button>
              <button
                onClick={() => changeLanguage('es')}
                className={`px-3 py-2 rounded-lg transition text-sm ${
                  i18n.language === 'es'
                    ? 'bg-white text-primary-600 font-semibold'
                    : 'bg-primary-700 hover:bg-primary-600'
                }`}
              >
                🇪🇸 ES
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition ${
                activeTab === 'dashboard'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('dashboard')}
            </button>
            <button
              onClick={() => setActiveTab('generate')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition ${
                activeTab === 'generate'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('generate')}
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition ${
                activeTab === 'history'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('history')}
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard key={refreshKey} />}
        {activeTab === 'generate' && <DocumentForm onGenerated={handleDocumentGenerated} />}
        {activeTab === 'history' && <History key={refreshKey} />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            ECM Document Generator - Sample Document Generation Tool
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
