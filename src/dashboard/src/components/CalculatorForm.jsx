import React from 'react';
import { useTranslation } from 'react-i18next';
import Input from './Input';
import Select from './Select';
import Checkbox from './Checkbox';
import Tooltip from './Tooltip';

const CalculatorForm = ({ state, dispatch, handleCalculate }) => {
  const { t } = useTranslation();
  const { b2bData, uopData, loading, calculationMode } = state;

  const handleB2bChange = (e) => {
    const { name, value, type, checked } = e.target;
    dispatch({ type: 'SET_B2B_FIELD', payload: { name, value, inputType: type, checked } });
  };

  const handleUopChange = (e) => {
    const { name, value, type, checked } = e.target;
    dispatch({ type: 'SET_UOP_FIELD', payload: { name, value, inputType: type, checked } });
  };

  const handleAgeChange = (e) => {
    dispatch({ type: 'SET_AGE', payload: parseInt(e.target.value, 10) });
  };

  const handleCalculationModeChange = (e) => {
    dispatch({ type: 'SET_CALCULATION_MODE', payload: e.target.value });
  };

  const zusOptions = [
    { value: 'start_relief', label: t('form.zus_start_relief') },
    { value: 'preferential', label: t('form.zus_preferential') },
    { value: 'full', label: t('form.zus_full') },
  ];

  const taxFormOptions = [
    { value: 'lump_sum_it', label: t('form.tax_flat_it') },
    { value: 'flat_tax', label: t('form.tax_linear') },
    { value: 'tax_scale', label: t('form.tax_scale') },
    { value: 'ip_box', label: t('form.tax_ip_box') },
  ];

  const ipBoxBaseOptions = [
    { value: 'flat_tax', label: t('form.ip_box_base_flat_tax') },
    { value: 'tax_scale', label: t('form.ip_box_base_tax_scale') },
  ];

  const benefitOptions = [
    { value: 'medical_care', label: t('form.benefit_medical') },
    { value: 'sport_card', label: t('form.benefit_sport') },
    { value: 'training_budget', label: t('form.benefit_training') },
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

      {/* Age Input */}
      <div className="md:col-span-2 bg-white p-6 rounded-lg shadow mb-8">
        <Input
          label={t('form.age')}
          id="age"
          name="age"
          type="number"
          value={b2bData.age} // Assuming age is the same for both, simplifies state
          onChange={handleAgeChange}
          data-testid="age-input"
        />
      </div>

      {/* B2B Section */}
      <div className="bg-gray-50 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6" data-testid="b2b-form-title">{t('form.b2b_title')}</h2>
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.financial_data')}</legend>
          <Input
            label={t('form.monthly_invoice')}
            id="monthly_invoice_amount"
            name="monthly_invoice_amount"
            type="number"
            value={b2bData.monthly_invoice_amount}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.business_costs')}
            id="monthly_business_costs"
            name="monthly_business_costs"
            type="number"
            value={b2bData.monthly_business_costs}
            onChange={handleB2bChange}
          />
          <Select
            label={t('form.zus_type')}
            id="zus_type"
            name="zus_type"
            value={b2bData.zus_type}
            onChange={handleB2bChange}
            options={zusOptions}
          />
          <Checkbox
            label={t('form.voluntary_sick_leave')}
            id="sickness_insurance"
            name="sickness_insurance"
            checked={b2bData.sickness_insurance}
            onChange={handleB2bChange}
          />
          <Select
            label={t('form.tax_form')}
            id="tax_form"
            name="tax_form"
            value={b2bData.tax_form}
            onChange={handleB2bChange}
            options={taxFormOptions}
          />
          {b2bData.tax_form === 'ip_box' && (
            <div className="mt-4">
              <Input
                label={t('form.ip_box_qualified_share')}
                id="ip_box_qualified_share"
                name="ip_box_qualified_share"
                type="number"
                min="0"
                max="100"
                step="1"
                value={b2bData.ip_box_qualified_share}
                onChange={handleB2bChange}
                description={t('form.ip_box_qualified_share_tooltip')}
              />
              <Select
                label={t('form.ip_box_base_form')}
                id="ip_box_base_form"
                name="ip_box_base_form"
                value={b2bData.ip_box_base_form}
                onChange={handleB2bChange}
                options={ipBoxBaseOptions}
              />
              <div
                role="alert"
                className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900"
              >
                {t('form.ip_box_warning')}
              </div>
            </div>
          )}
        </fieldset>
        <fieldset className="border border-gray-200 p-4 rounded-md mb-6">
          <legend className="text-lg font-semibold text-gray-700 px-2">{t('form.time_off_stoppage')}</legend>
          <Input
            label={t('form.unpaid_vacation')}
            id="vacation_days"
            name="vacation_days"
            type="number"
            value={b2bData.vacation_days}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.unpaid_sick')}
            id="sick_days"
            name="sick_days"
            type="number"
            value={b2bData.sick_days}
            onChange={handleB2bChange}
          />
          <Input
            label={t('form.stoppage_months')}
            id="stoppage_months"
            name="stoppage_months"
            type="number"
            value={b2bData.stoppage_months}
            onChange={handleB2bChange}
          />
        </fieldset>
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
              label={t('form.paid_vacation_days_label')}
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
              label={t('form.paid_sick_days_label')}
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
              label={t('form.medical_care_value_label')}
              id="companyBenefits.medicalCare.value"
              type="number"
              value={b2bData.companyBenefits.medicalCare.value}
              onChange={handleB2bChange}
              className="ml-6"
              data-testid="medical-care-input"
            />
          )}
          <Checkbox
            label={t('form.company_life_cover')}
            id="companyBenefits.lifeInsurance.enabled"
            checked={b2bData.companyBenefits.lifeInsurance.enabled}
            onChange={handleB2bChange}
            data-testid="life-insurance-checkbox"
          />
          {b2bData.companyBenefits.lifeInsurance.enabled && (
            <Input
              label={t('form.life_insurance_value_label')}
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
              label={t('form.sport_card_value_label')}
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
              label={t('form.training_budget_value_label')}
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
              label={t('form.other_benefits_value_label')}
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
            id="monthly_gross_salary"
            name="monthly_gross_salary"
            type="number"
            value={uopData.monthly_gross_salary}
            onChange={handleUopChange}
          />
          <div className="flex items-center">
            <Select
              label={t('form.kup_type')}
              id="deductible_cost_settings.type"
              name="deductible_cost_settings.type"
              value={uopData.deductible_cost_settings.type}
              onChange={handleUopChange}
              options={[
                { value: 'standard', label: t('form.kup_standard') },
                { value: 'elevated', label: t('form.kup_elevated') },
                { value: 'author_50', label: t('form.kup_creative_50') },
                { value: 'none', label: t('form.kup_none') },
              ]}
            />
            <Tooltip text={t(`form.kup_${uopData.deductible_cost_settings.type}_tooltip`)}>
              <span className="ml-2 text-gray-500 cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </span>
            </Tooltip>
          </div>
          {uopData.deductible_cost_settings.type === 'author_50' && (
            <Input
              label={t('form.creative_work_percentage')}
              id="deductible_cost_settings.creative_work_percentage"
              name="deductible_cost_settings.creative_work_percentage"
              type="number"
              value={uopData.deductible_cost_settings.creative_work_percentage}
              onChange={handleUopChange}
              className="ml-4 mt-2"
            />
          )}
          <Checkbox
            label={t('form.youth_relief')}
            id="youth_relief"
            name="youth_relief"
            checked={uopData.youth_relief}
            onChange={handleUopChange}
            data-testid="youth-relief-uop"
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
              name="selected_benefits"
              value={option.value}
              checked={uopData.selected_benefits.includes(option.value)}
              onChange={handleUopChange}
            />
          ))}
        </fieldset>
      </div>

      <div className="md:col-span-2 flex justify-center mt-8">
        <button
          onClick={handleCalculate}
          disabled={loading}
          data-testid="calculate-button"
          className="w-full md:w-auto bg-primary hover:bg-blue-800 text-white font-bold py-3 px-8 rounded-lg text-lg transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 shadow-lg"
          aria-label={t('form.calculate_button')}
        >
          {loading ? t('form.loading_button') : t('form.calculate_button')}
        </button>
      </div>
    </div>
  );
};

export default CalculatorForm;
