import React from 'react';
import { useTranslation } from 'react-i18next';
import Input from './Input';
import Select from './Select';
import Checkbox from './Checkbox';
import InsuranceConfigurator from './InsuranceConfigurator';

const CalculatorForm = ({ b2bData, uopData, handleB2bChange, handleUopChange, handleCalculate, loading, calculationMode, handleCalculationModeChange, insuranceConfig, setInsuranceConfig }) => {
  const { t } = useTranslation();

  const zusOptions = [
    { value: 'mala_firma', label: t('form.zus_preferential') },
    { value: 'duza_firma', label: t('form.zus_full') },
  ];

  const taxFormOptions = [
    { value: 'ryczalt_IT', label: t('form.tax_flat_it') },
    { value: 'liniowy', label: t('form.tax_linear') },
    { value: 'skala', label: t('form.tax_scale') },
    { value: 'ip_box', label: t('form.tax_ip_box') },
  ];

  const benefitOptions = [
    { value: 'opieka_medyczna', label: t('form.benefit_medical') },
    { value: 'karta_sportowa', label: t('form.benefit_sport') },
    { value: 'ubezpieczenie_na_zycie', label: t('form.benefit_life') },
    { value: 'szkolenia', label: t('form.benefit_training') },
    { value: 'ppk', label: t('form.benefit_ppk') },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Calculation Mode Selection */}
      <div className="md:col-span-2 bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t('form.calculation_mode_title')}</h2>
        <div className="flex items-center space-x-4">
          <label className="inline-flex items-center">
            <input
              type="radio"
              className="form-radio text-primary"
              name="calculationMode"
              value="uop_to_b2b"
              checked={calculationMode === 'uop_to_b2b'}
              onChange={handleCalculationModeChange}
              data-testid="uop-to-b2b-radio"
            />
            <span className="ml-2 text-gray-700">{t('form.uop_to_b2b_mode')}</span>
          </label>
          <label className="inline-flex items-center">
            <input
              type="radio"
              className="form-radio text-primary"
              name="calculationMode"
              value="b2b_to_uop"
              checked={calculationMode === 'b2b_to_uop'}
              onChange={handleCalculationModeChange}
              data-testid="b2b-to-uop-radio"
            />
            <span className="ml-2 text-gray-700">{t('form.b2b_to_uop_mode')}</span>
          </label>
        </div>
      </div>

      {/* B2B Section */}
      <div className="bg-gray-50 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6" data-testid="b2b-form-title">{t('form.b2b_title')}</h2>
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.financial_data')}</legend>
          <Input
            label={t('form.monthly_invoice')}
            id="faktura_miesieczna"
            type="number"
            value={b2bData.faktura_miesieczna}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.business_costs')}
            id="koszty_firmowe_miesieczne"
            type="number"
            value={b2bData.koszty_firmowe_miesieczne}
            onChange={handleB2bChange}
          />
          <Select
            label={t('form.zus_type')}
            id="zus_rodzaj"
            value={b2bData.zus_rodzaj}
            onChange={handleB2bChange}
            options={zusOptions}
          />
          <Checkbox
            label={t('form.voluntary_sick_leave')}
            id="zus_chorobowe"
            checked={b2bData.zus_chorobowe}
            onChange={handleB2bChange}
          />
          <Select
            label={t('form.tax_form')}
            id="forma_opodatkowania"
            value={b2bData.forma_opodatkowania}
            onChange={handleB2bChange}
            options={taxFormOptions}
          />
          <Checkbox
            label={t('form.youth_relief')}
            id="ulga_dla_mlodych"
            checked={b2bData.ulga_dla_mlodych}
            onChange={handleB2bChange}
          />
          <Checkbox
            label={t('form.equalize_pension')}
            id="equalizePension"
            checked={b2bData.equalizePension}
            onChange={handleB2bChange}
            disabled={!uopData.wynagrodzenie_brutto}
          />
        </fieldset>
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.time_off_stoppage')}</legend>
          <Input
            label={t('form.unpaid_vacation')}
            id="urlop_dni"
            type="number"
            value={b2bData.urlop_dni}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.unpaid_sick')}
            id="chorobowe_dni"
            type="number"
            value={b2bData.chorobowe_dni}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.stoppage_months')}
            id="przestoje_miesiace"
            type="number"
            value={b2bData.przestoje_miesiace}
            onChange={handleB2bChange}
          />
        </fieldset>
        <InsuranceConfigurator 
            insuranceConfig={insuranceConfig} 
            setInsuranceConfig={setInsuranceConfig} 
            b2bMonthlyInvoice={b2bData.faktura_miesieczna} 
        />
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.benefits')}</legend>
          <Input
            label={t('form.custom_benefits_value')}
            id="customBenefits"
            type="number"
            value={b2bData.customBenefits}
            onChange={handleB2bChange}
          />

          <h3 className="text-xl font-semibold text-gray-700 mt-6 mb-4">{t('form.company_benefits')}</h3>
          <Checkbox
            label={t('form.paid_vacation')}
            id="companyBenefits.paidVacationDays.enabled"
            checked={b2bData.companyBenefits.paidVacationDays.enabled}
            onChange={handleB2bChange}
            data-testid="paid-vacation-checkbox"
          />
          {b2bData.companyBenefits.paidVacationDays.enabled && (
            <Input
              label={t('form.paid_vacation').replace(' (from company)', '') + ' Days'}
              id="companyBenefits.paidVacationDays.days"
              type="number"
              value={b2bData.companyBenefits.paidVacationDays.days}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="paid-vacation-input"
            />
          )}
          <Checkbox
            label={t('form.paid_sick')}
            id="companyBenefits.paidSickDays.enabled"
            checked={b2bData.companyBenefits.paidSickDays.enabled}
            onChange={handleB2bChange}
            data-testid="paid-sick-checkbox"
          />
          {b2bData.companyBenefits.paidSickDays.enabled && (
            <Input
              label={t('form.paid_sick').replace(' (from company)', '') + ' Days'}
              id="companyBenefits.paidSickDays.days"
              type="number"
              value={b2bData.companyBenefits.paidSickDays.days}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="paid-sick-input"
            />
          )}
          <Checkbox
            label={t('form.medical_care')}
            id="companyBenefits.medicalCare.enabled"
            checked={b2bData.companyBenefits.medicalCare.enabled}
            onChange={handleB2bChange}
            data-testid="medical-care-checkbox"
          />
          {b2bData.companyBenefits.medicalCare.enabled && (
            <Input
              label={t('form.medical_care').replace(' (from company)', '') + ' Value (PLN/year)'}
              id="companyBenefits.medicalCare.value"
              type="number"
              value={b2bData.companyBenefits.medicalCare.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="medical-care-input"
            />
          )}
          <Checkbox
            label={t('form.life_insurance')}
            id="companyBenefits.lifeInsurance.enabled"
            checked={b2bData.companyBenefits.lifeInsurance.enabled}
            onChange={handleB2bChange}
            data-testid="life-insurance-checkbox"
          />
          {b2bData.companyBenefits.lifeInsurance.enabled && (
            <Input
              label={t('form.life_insurance').replace(' (from company)', '') + ' Value (PLN/year)'}
              id="companyBenefits.lifeInsurance.value"
              type="number"
              value={b2bData.companyBenefits.lifeInsurance.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="life-insurance-input"
            />
          )}
          <Checkbox
            label={t('form.sport_card')}
            id="companyBenefits.sportCard.enabled"
            checked={b2bData.companyBenefits.sportCard.enabled}
            onChange={handleB2bChange}
            data-testid="sport-card-checkbox"
          />
          {b2bData.companyBenefits.sportCard.enabled && (
            <Input
              label={t('form.sport_card').replace(' (from company)', '') + ' Value (PLN/year)'}
              id="companyBenefits.sportCard.value"
              type="number"
              value={b2bData.companyBenefits.sportCard.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="sport-card-input"
            />
          )}
          <Checkbox
            label={t('form.training_budget')}
            id="companyBenefits.trainingBudget.enabled"
            checked={b2bData.companyBenefits.trainingBudget.enabled}
            onChange={handleB2bChange}
            data-testid="training-budget-checkbox"
          />
          {b2bData.companyBenefits.trainingBudget.enabled && (
            <Input
              label={t('form.training_budget').replace(' (from company)', '') + ' Value (PLN/year)'}
              id="companyBenefits.trainingBudget.value"
              type="number"
              value={b2bData.companyBenefits.trainingBudget.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="training-budget-input"
            />
          )}
          <Checkbox
            label={t('form.other_benefits')}
            id="companyBenefits.otherBenefits.enabled"
            checked={b2bData.companyBenefits.otherBenefits.enabled}
            onChange={handleB2bChange}
            data-testid="other-benefits-checkbox"
          />
          {b2bData.companyBenefits.otherBenefits.enabled && (
            <Input
              label={t('form.other_benefits').replace(' (from company)', '') + ' Value (PLN/year)'}
              id="companyBenefits.otherBenefits.value"
              type="number"
              value={b2bData.companyBenefits.otherBenefits.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="other-benefits-input"
            />
          )}
        </fieldset>
      </div>

      {/* UoP Section */}
      <div className="bg-gray-50 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">{t('form.uop_title')}</h2>
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.financial_data')}</legend>
          <Input
            label={t('form.gross_salary')}
            id="wynagrodzenie_brutto"
            type="number"
            value={uopData.wynagrodzenie_brutto}
            onChange={handleUopChange}
          />
          <Select
            label={t('form.kup_type')}
            id="kup_settings.type"
            name="kup_settings.type"
            value={uopData.kup_settings.type}
            onChange={handleUopChange}
            options={[
              { value: 'standard', label: t('form.kup_standard') },
              { value: 'elevated', label: t('form.kup_elevated') },
              { value: 'autorskie_50', label: t('form.kup_creative_50') },
              { value: 'brak', label: t('form.kup_none') },
            ]}
          />
          {uopData.kup_settings.type === 'autorskie_50' && (
            <Input
              label={t('form.creative_work_percentage')}
              id="kup_settings.creative_work_percentage"
              name="kup_settings.creative_work_percentage"
              type="number"
              value={uopData.kup_settings.creative_work_percentage}
              onChange={handleUopChange}
              className="ml-4 mt-2"
            />
          )}
          <Checkbox
            label={t('form.youth_relief')}
            id="ulga_dla_mlodych"
            checked={uopData.ulga_dla_mlodych}
            onChange={handleUopChange}
          />
        </fieldset>

        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.benefits')}</legend>
          <h3 className="text-xl font-semibold text-gray-700 mt-6 mb-4">{t('form.selected_benefits')}</h3>
          {benefitOptions.map((option) => (
            <Checkbox
              key={option.value}
              label={option.label}
              id={option.value}
              name="wybrane_benefity"
              value={option.value}
              checked={uopData.wybrane_benefity.includes(option.value)}
              onChange={handleUopChange}
            />
          ))}
        </fieldset>
      </div>

      <div className="md:col-span-2 flex justify-center mt-8">
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="w-full md:w-auto bg-primary hover:bg-blue-800 text-white font-bold py-3 px-8 rounded-lg text-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 shadow-lg"
        >
          {loading ? 'Calculating...' : t('form.calculate_button')}
        </button>
      </div>
    </div>
  );
};

export default CalculatorForm;