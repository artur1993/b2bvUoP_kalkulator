import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { useTranslation } from "react-i18next";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

const ComparisonChart = ({
  results,
  barChartRef,
  b2bStackedBarRef,
  uopStackedBarRef,
}) => {
  const { t } = useTranslation();

  if (!results) return null;

  const { b2b_results, uop_results } = results;

  // Bar Chart Data
  const barChartData = {
    labels: [t("charts.total_comparison_title")],
    datasets: [
      {
        label: t("form.uop_title"),
        data: [uop_results.total_annual_value],
        backgroundColor: "#4fd1c5", // secondary
      },
      {
        label: t("form.b2b_title"),
        data: [b2b_results.total_annual_value],
        backgroundColor: "#2c5282", // primary
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: t("charts.total_comparison_title"),
      },
    },
  };

  // Stacked Bar Chart Data for B2B Breakdown
  const b2bStackedBarData = {
    labels: [t("charts.b2b_breakdown_title")],
    datasets: [
      {
        label: t("charts.net_income"),
        data: [b2b_results.annual_net_income],
        backgroundColor: "#4CAF50", // Green
      },
      {
        label: t("charts.zus"),
        data: [b2b_results.annual_zus],
        backgroundColor: "#FFC107", // Amber
      },
      {
        label: t("charts.tax"),
        data: [b2b_results.annual_tax],
        backgroundColor: "#FF9800", // Orange
      },
      {
        label: t("charts.business_costs"),
        data: [b2b_results.annual_business_costs],
        backgroundColor: "#9E9E9E", // Grey
      },
      {
        label: t("charts.lost_revenue"),
        data: [b2b_results.annual_lost_revenue],
        backgroundColor: "#F44336", // Red
      },
      {
        label: t("charts.company_benefits"),
        data: [b2b_results.annual_company_benefits_value],
        backgroundColor: "#2196F3", // Blue
      },
      {
        label: t("charts.custom_benefits"),
        data: [b2b_results.annual_custom_benefits_value],
        backgroundColor: "#9C27B0", // Purple
      },
    ],
  };

  const b2bStackedBarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: t("charts.b2b_breakdown_title"),
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
    labels: [t("charts.uop_breakdown_title")],
    datasets: [
      {
        label: t("charts.net_income"),
        data: [uop_results.annual_net_income],
        backgroundColor: "#4CAF50", // Green
      },
      {
        label: t("charts.zus"),
        data: [uop_results.annual_zus],
        backgroundColor: "#FFC107", // Amber
      },
      {
        label: t("charts.tax"),
        data: [uop_results.annual_tax],
        backgroundColor: "#FF9800", // Orange
      },
      {
        label: t("charts.benefits"),
        data: [uop_results.annual_benefits_value],
        backgroundColor: "#2196F3", // Blue
      },
    ],
  };

  const uopStackedBarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: t("charts.uop_breakdown_title"),
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
    <div
      className="mt-10 p-6 bg-white rounded-lg shadow-lg"
      data-testid="comparison-chart-section"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Bar
            data={barChartData}
            options={barChartOptions}
            ref={barChartRef}
            aria-label={t("charts.total_comparison_title")}
          />
        </div>
        <div>
          <Bar
            data={b2bStackedBarData}
            options={b2bStackedBarOptions}
            ref={b2bStackedBarRef}
            aria-label={t("charts.b2b_breakdown_title")}
          />
        </div>
        <div>
          <Bar
            data={uopStackedBarData}
            options={uopStackedBarOptions}
            ref={uopStackedBarRef}
            aria-label={t("charts.uop_breakdown_title")}
          />
        </div>
      </div>
    </div>
  );
};

export default ComparisonChart;
