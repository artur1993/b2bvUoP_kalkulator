import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5001/api'; // Flask API prefix

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
