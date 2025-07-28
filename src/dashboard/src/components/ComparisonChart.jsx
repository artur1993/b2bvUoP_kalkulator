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
  if (!results) return null;

  const { b2b_results, uop_results } = results;

  // Bar Chart Data
  const barChartData = {
    labels: ['Total Annual Value'],
    datasets: [
      {
        label: 'UoP',
        data: [uop_results.calkowita_roczna_wartosc],
        backgroundColor: '#4fd1c5', // secondary
      },
      {
        label: 'B2B',
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
        text: 'Total Annual Value Comparison',
      },
    },
  };

  // Stacked Bar Chart Data for B2B Breakdown
  const b2bStackedBarData = {
    labels: ['B2B Breakdown'],
    datasets: [
      {
        label: 'Net Income',
        data: [b2b_results.roczne_netto_na_reke],
        backgroundColor: '#4CAF50', // Green
      },
      {
        label: 'ZUS',
        data: [b2b_results.roczny_zus],
        backgroundColor: '#FFC107', // Amber
      },
      {
        label: 'Tax',
        data: [b2b_results.roczny_podatek],
        backgroundColor: '#FF9800', // Orange
      },
      {
        label: 'Business Costs',
        data: [b2b_results.roczne_koszty_firmowe],
        backgroundColor: '#9E9E9E', // Grey
      },
      {
        label: 'Lost Revenue',
        data: [b2b_results.roczny_utracony_przychod],
        backgroundColor: '#F44336', // Red
      },
      {
        label: 'Company Benefits',
        data: [b2b_results.roczna_wartosc_benefitow_od_firmy],
        backgroundColor: '#2196F3', // Blue
      },
      {
        label: 'Custom Benefits',
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
        text: 'B2B Annual Value Breakdown',
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
    labels: ['UoP Breakdown'],
    datasets: [
      {
        label: 'Net Income',
        data: [uop_results.roczne_netto_na_reke],
        backgroundColor: '#4CAF50', // Green
      },
      {
        label: 'ZUS',
        data: [uop_results.roczny_zus],
        backgroundColor: '#FFC107', // Amber
      },
      {
        label: 'Tax',
        data: [uop_results.roczny_podatek],
        backgroundColor: '#FF9800', // Orange
      },
      {
        label: 'Benefits',
        data: [uop_results.roczna_wartosc_benefitow],
        backgroundColor: '#2196F3', // Blue
      },
      {
        label: 'Paid Days Off',
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
        text: 'UoP Annual Value Breakdown',
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
