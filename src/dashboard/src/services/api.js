import axios from 'axios';

const API_BASE_URL = '/api'; // Flask API prefix

const handleError = (error, context) => {
  console.error(`Error in ${context}:`, error.response ? error.response.data : error.message);
  throw error;
};

export const calculateResults = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'calculateResults');
  }
};

export const exportToExcel = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/excel`, data, {
      responseType: 'blob', // Important for handling binary data
    });
    return response.data;
  } catch (error) {
    handleError(error, 'exportToExcel');
  }
};

export const exportToPdf = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/pdf`, data, {
      responseType: 'blob', // Important for handling binary data
    });
    return response.data;
  } catch (error) {
    handleError(error, 'exportToPdf');
  }
};

export const exportToAdvancedPdf = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/pdf/advanced`, data, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    handleError(error, 'exportToAdvancedPdf');
  }
};

export const calculateBreakEvenAnalysis = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate/break-even-analysis`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'calculateBreakEvenAnalysis');
  }
};

export const calculateSensitivityAnalysis = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate/sensitivity-analysis`, data);
    return response.data;
  } catch (error) {
    handleError(error, 'calculateSensitivityAnalysis');
  }
};