import React from "react";
import { useTranslation } from "react-i18next";

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex space-x-2">
      <button
        onClick={() => changeLanguage("pl")}
        className={`px-3 py-1 rounded-md text-sm font-medium ${i18n.language === "pl" ? "bg-primary text-white" : "bg-gray-200 text-gray-700"}`}
      >
        PL
      </button>
      <button
        onClick={() => changeLanguage("en")}
        className={`px-3 py-1 rounded-md text-sm font-medium ${i18n.language === "en" ? "bg-primary text-white" : "bg-gray-200 text-gray-700"}`}
      >
        EN
      </button>
    </div>
  );
};

export default LanguageSwitcher;
