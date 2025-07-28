import React from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const Header = () => {
  const { t } = useTranslation();

  return (
    <header className="bg-surface w-full py-4 shadow-md mb-8">
      <div className="container mx-auto px-6 flex justify-between items-center">
        <div className="text-left">
          <h1 className="text-3xl font-bold text-primary">
            {t('header.title')}
          </h1>
          <p className="text-gray-600">{t('header.subtitle')}</p>
        </div>
        <LanguageSwitcher />
      </div>
    </header>
  );
};

export default Header;