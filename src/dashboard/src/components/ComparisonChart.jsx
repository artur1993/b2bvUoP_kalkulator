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
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'B2B',
        data: [b2b_results.calkowita_roczna_wartosc],
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
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

  // Pie Chart Data (B2B Breakdown)
  const pieChartData = {
    labels: [
      'Net Income',
      'ZUS',
      'Tax',
      'Business Costs',
      'Lost Revenue',
      'Company Benefits',
      'Custom Benefits',
    ],
    datasets: [
      {
        data: [
          b2b_results.roczne_netto_na_reke,
          b2b_results.roczny_zus,
          b2b_results.roczny_podatek,
          b2b_results.roczne_koszty_firmowe,
          b2b_results.roczny_utracony_przychod,
          b2b_results.roczna_wartosc_benefitow_od_firmy,
          b2b_results.roczna_wartosc_wlasnych_korzysci,
        ],
        backgroundColor: [
          '#4CAF50', // Green for Net Income
          '#FFC107', // Amber for ZUS
          '#FF9800', // Orange for Tax
          '#9E9E9E', // Grey for Business Costs
          '#F44336', // Red for Lost Revenue
          '#2196F3', // Blue for Company Benefits
          '#9C27B0', // Purple for Custom Benefits
        ],
        borderColor: [
          '#ffffff',
          '#ffffff',
          '#ffffff',
          '#ffffff',
          '#ffffff',
          '#ffffff',
          '#ffffff',
        ],
        borderWidth: 1,
      },
    ],
  };

  const pieChartOptions = {
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
  };

  return (
    <div className="mt-10 p-6 bg-white rounded-lg shadow-lg">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Bar data={barChartData} options={barChartOptions} />
        </div>
        <div>
          <Pie data={pieChartData} options={pieChartOptions} />
        </div>
      </div>
    </div>
  );
};

export default ComparisonChart;