import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import translationFR from './fr.json';
import translationDE from './de.json';
import translationENGB from './en-GB.json';
import translationENUS from './en-US.json';
import translationES from './es.json';
import translationIT from './it.json';

const resources = {
  fr: {
    translation: translationFR
  },
  de: {
    translation: translationDE
  },
  'en-GB': {
    translation: translationENGB
  },
  'en-US': {
    translation: translationENUS
  },
  es: {
    translation: translationES
  },
  it: {
    translation: translationIT
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en-GB',
    fallbackLng: 'en-GB',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
