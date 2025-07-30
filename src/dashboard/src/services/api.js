import axios from 'axios';

const API_BASE_URL = '/api'; // Flask API prefix

export const calculateResults = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate`, data);
    return response.data;
  } catch (error) {
    
    throw error;
  }
};

export const exportToExcel = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/excel`, data, {
      responseType: 'blob', // Important for handling binary data
    });
    return response.data;
  } catch (error) {
    
    throw error;
  }
};

export const exportToPdf = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/pdf`, data, {
      responseType: 'blob', // Important for handling binary data
    });
    return response.data;
  } catch (error) {
    
    throw error;
  }
};

export const exportToAdvancedPdf = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/export/pdf/advanced`, data, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting to Advanced PDF:', error);
    throw error;
  }
};

export const calculateBreakEvenAnalysis = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate/break-even-analysis`, data);
    return response.data;
  } catch (error) {
    console.error('Error fetching break-even data:', error);
    throw error;
  }
};

export const calculateSensitivityAnalysis = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/calculate/sensitivity-analysis`, data);
    return response.data;
  } catch (error) {
    console.error('Error fetching sensitivity data:', error);
    throw error;
  }
};