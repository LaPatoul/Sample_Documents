import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import translationFR from './fr.json';
import translationDE from './de.json';

const resources = {
  fr: {
    translation: translationFR
  },
  de: {
    translation: translationDE
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fr',
    fallbackLng: 'fr',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
