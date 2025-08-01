import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { insuranceModules, insuranceProfiles } from '../data/insuranceOptions';
import Checkbox from './Checkbox';
import Select from './Select';
import Tooltip from './Tooltip';

/**
 * A component for configuring a B2B insurance package.
 * It allows users to select pre-defined profiles or customize their own package.
 * @param {object} props - The component props.
 * @param {object} props.insuranceConfig - The current insurance configuration state.
 * @param {function} props.setInsuranceConfig - The function to update the insurance configuration state.
 * @param {number} props.b2bMonthlyInvoice - The monthly B2B invoice amount, used for dynamic cost calculations.
 */
const InsuranceConfigurator = ({ insuranceConfig, setInsuranceConfig, b2bMonthlyInvoice }) => {
  const { t } = useTranslation();
  const [totalCost, setTotalCost] = useState(0);

  const calculateModuleCost = (moduleId, selections, b2bMonthlyInvoice) => {
    const config = selections[moduleId];
    const module = insuranceModules[moduleId];
    if (config.enabled && module) {
      const option = module.options[config.level];
      if (module.type === 'dynamic') {
        const annualIncome = b2bMonthlyInvoice * 12;
        return (annualIncome * option.multiplier) / 12;
      } else {
        return option.cost;
      }
    }
    return 0;
  };

  const calculateTotalCost = (selections) => {
    let cost = 0;
    for (const moduleId in selections) {
      cost += calculateModuleCost(moduleId, selections, b2bMonthlyInvoice);
    }
    return cost;
  };

  useEffect(() => {
    const newTotalCost = calculateTotalCost(insuranceConfig.selections);
    setTotalCost(newTotalCost);
  }, [insuranceConfig, b2bMonthlyInvoice]);

  const handleProfileChange = (profileName) => {
    setInsuranceConfig(prev => ({
      ...prev,
      activeProfile: profileName,
      selections: insuranceProfiles[profileName]
    }));
  };

  const handleSelectionChange = (moduleId, field, value) => {
    setInsuranceConfig(prev => ({
      ...prev,
      activeProfile: 'custom',
      selections: {
        ...prev.selections,
        [moduleId]: {
          ...prev.selections[moduleId],
          [field]: value
        }
      }
    }));
  };

  return (
    <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
      <legend className="text-lg font-semibold text-gray-700 px-2">{t('insurance.title')}</legend>
      <div className="flex justify-between items-center mb-4">
        <div className="flex space-x-2">
          {['minimal', 'standard', 'premium'].map(profile => (
            <button 
              key={profile}
              onClick={() => handleProfileChange(profile)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${insuranceConfig.activeProfile === profile ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              aria-label={`${t('insurance.profiles.' + profile)} profile`}
            >
              {t(`insurance.profiles.${profile}`)}
            </button>
          ))}
        </div>
        <div className="text-lg font-semibold">
          {t('insurance.total_cost')}: {totalCost.toFixed(2)} PLN
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(insuranceModules).map(([id, module]) => (
          <div key={id} className="border border-gray-200 p-3 rounded-md">
            <div className="module-header">
              <div className="module-title-wrapper">
                <Checkbox
                  label={module.name}
                  id={`insurance.${id}.enabled`}
                  checked={insuranceConfig.selections[id]?.enabled || false}
                  onChange={(e) => handleSelectionChange(id, 'enabled', e.target.checked)}
                />
                <Tooltip text={t(module.tooltip, { ns: 'insurance' })}>
                  <span className="ml-2 text-gray-500 cursor-pointer">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </span>
                </Tooltip>
              </div>
              {insuranceConfig.selections[id]?.enabled && (
                <span className="module-cost">
                  {calculateModuleCost(id, insuranceConfig.selections, b2bMonthlyInvoice).toFixed(2)} zł/mies.
                </span>
              )}
            </div>
            {insuranceConfig.selections[id]?.enabled && (
              <Select
                id={`insurance.${id}.level`}
                value={insuranceConfig.selections[id].level}
                onChange={(e) => handleSelectionChange(id, 'level', e.target.value)}
                options={Object.keys(module.options).map(key => ({ value: key, label: t(`insurance.options.${key}`, key) }))}
                className="mt-2"
              />
            )}
          </div>
        ))}
      </div>
    </fieldset>
  );
};

export default InsuranceConfigurator;