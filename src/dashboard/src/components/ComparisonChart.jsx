import React from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { useTranslation } from 'react-i18next';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ComparisonChart = ({ results }) => {
  const { t } = useTranslation();

  if (!results) return null;

  const { b2b_results, uop_results } = results;

  // Bar Chart Data
  const barChartData = {
    labels: [t('charts.total_comparison_title')],
    datasets: [
      {
        label: t('form.uop_title'),
        data: [uop_results.calkowita_roczna_wartosc],
        backgroundColor: '#4fd1c5', // secondary
      },
      {
        label: t('form.b2b_title'),
        data: [b2b_results.calkowita_roczna_wartosc],
        backgroundColor: '#2c5282', // primary
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: t('charts.total_comparison_title'),
      },
    },
  };

  // Stacked Bar Chart Data for B2B Breakdown
  const b2bStackedBarData = {
    labels: [t('charts.b2b_breakdown_title')],
    datasets: [
      {
        label: t('charts.net_income'),
        data: [b2b_results.roczne_netto_na_reke],
        backgroundColor: '#4CAF50', // Green
      },
      {
        label: t('charts.zus'),
        data: [b2b_results.roczny_zus],
        backgroundColor: '#FFC107', // Amber
      },
      {
        label: t('charts.tax'),
        data: [b2b_results.roczny_podatek],
        backgroundColor: '#FF9800', // Orange
      },
      {
        label: t('charts.business_costs'),
        data: [b2b_results.roczne_koszty_firmowe],
        backgroundColor: '#9E9E9E', // Grey
      },
      {
        label: t('charts.lost_revenue'),
        data: [b2b_results.roczny_utracony_przychod],
        backgroundColor: '#F44336', // Red
      },
      {
        label: t('charts.company_benefits'),
        data: [b2b_results.roczna_wartosc_benefitow_od_firmy],
        backgroundColor: '#2196F3', // Blue
      },
      {
        label: t('charts.custom_benefits'),
        data: [b2b_results.roczna_wartosc_wlasnych_korzysci],
        backgroundColor: '#9C27B0', // Purple
      },
    ],
  };

  const b2bStackedBarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: t('charts.b2b_breakdown_title'),
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
      },
    },
  };

  // Stacked Bar Chart Data for UoP Breakdown
  const uopStackedBarData = {
    labels: [t('charts.uop_breakdown_title')],
    datasets: [
      {
        label: t('charts.net_income'),
        data: [uop_results.roczne_netto_na_reke],
        backgroundColor: '#4CAF50', // Green
      },
      {
        label: t('charts.zus'),
        data: [uop_results.roczny_zus],
        backgroundColor: '#FFC107', // Amber
      },
      {
        label: t('charts.tax'),
        data: [uop_results.roczny_podatek],
        backgroundColor: '#FF9800', // Orange
      },
      {
        label: t('charts.benefits'),
        data: [uop_results.roczna_wartosc_benefitow],
        backgroundColor: '#2196F3', // Blue
      },
      {
        label: t('charts.paid_days_off'),
        data: [uop_results.roczna_wartosc_platnych_dni_wolnych],
        backgroundColor: '#9C27B0', // Purple
      },
    ],
  };

  const uopStackedBarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: t('charts.uop_breakdown_title'),
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
      },
    },
  };

  return (
    <div className="mt-10 p-6 bg-white rounded-lg shadow-lg" data-testid="comparison-chart-section">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Bar data={barChartData} options={barChartOptions} />
        </div>
        <div>
          <Bar data={b2bStackedBarData} options={b2bStackedBarOptions} />
        </div>
        <div>
          <Bar data={uopStackedBarData} options={uopStackedBarOptions} />
        </div>
      </div>
    </div>
  );
};

export default ComparisonChart;
