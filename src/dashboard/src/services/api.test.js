import { describe, it, expect, vi } from 'vitest';
import axios from 'axios';
import { calculateResults, exportToExcel, calculateBreakEvenAnalysis, calculateSensitivityAnalysis } from './api';

// Mock axios
vi.mock('axios');

describe('API Service', () => {
  it('calculate sends correct data and returns response', async () => {
    const mockData = { b2b: {}, uop: {} };
    const mockResponse = { data: { b2b_results: {}, uop_results: {} } };
    axios.post.mockResolvedValue(mockResponse);

    const result = await calculateResults(mockData);

    expect(axios.post).toHaveBeenCalledWith('/api/calculate', mockData);
    expect(result).toEqual(mockResponse.data);
  });

  it('calculate handles errors', async () => {
    const mockData = { b2b: {}, uop: {} };
    const errorMessage = 'Network Error';
    axios.post.mockRejectedValue(new Error(errorMessage));

    await expect(calculateResults(mockData)).rejects.toThrow(errorMessage);
    expect(axios.post).toHaveBeenCalledWith('/api/calculate', mockData);
  });

  it('exportToExcel sends correct data and returns response', async () => {
    const mockResults = { b2b_results: {}, uop_results: {} };
    const mockResponse = { data: 'excel_blob' };
    axios.post.mockResolvedValue(mockResponse);

    const result = await exportToExcel(mockResults);

    expect(axios.post).toHaveBeenCalledWith('/api/export/excel', mockResults, {
      responseType: 'blob',
    });
    expect(result).toEqual(mockResponse.data);
  });

  it('exportToExcel handles errors', async () => {
    const mockResults = { b2b_results: {}, uop_results: {} };
    const errorMessage = 'Export Excel Error';
    axios.post.mockRejectedValue(new Error(errorMessage));

    await expect(exportToExcel(mockResults)).rejects.toThrow(errorMessage);
    expect(axios.post).toHaveBeenCalledWith('/api/export/excel', mockResults, {
      responseType: 'blob',
    });
  });

  it('calculateBreakEvenAnalysis sends correct data and returns response', async () => {
    const mockData = { b2b: {}, uop: {} };
    const mockResponse = { data: [] };
    axios.post.mockResolvedValue(mockResponse);

    const result = await calculateBreakEvenAnalysis(mockData);

    expect(axios.post).toHaveBeenCalledWith('/api/calculate/break-even-analysis', mockData);
    expect(result).toEqual(mockResponse.data);
  });

  it('calculateBreakEvenAnalysis handles errors', async () => {
    const mockData = { b2b: {}, uop: {} };
    const errorMessage = 'Break Even Analysis Error';
    axios.post.mockRejectedValue(new Error(errorMessage));

    await expect(calculateBreakEvenAnalysis(mockData)).rejects.toThrow(errorMessage);
    expect(axios.post).toHaveBeenCalledWith('/api/calculate/break-even-analysis', mockData);
  });

  it('calculateSensitivityAnalysis sends correct data and returns response', async () => {
    const mockData = { b2b: {}, uop: {} };
    const mockResponse = { data: [] };
    axios.post.mockResolvedValue(mockResponse);

    const result = await calculateSensitivityAnalysis(mockData);

    expect(axios.post).toHaveBeenCalledWith('/api/calculate/sensitivity-analysis', mockData);
    expect(result).toEqual(mockResponse.data);
  });

  it('calculateSensitivityAnalysis handles errors', async () => {
    const mockData = { b2b: {}, uop: {} };
    const errorMessage = 'Sensitivity Analysis Error';
    axios.post.mockRejectedValue(new Error(errorMessage));

    await expect(calculateSensitivityAnalysis(mockData)).rejects.toThrow(errorMessage);
    expect(axios.post).toHaveBeenCalledWith('/api/calculate/sensitivity-analysis', mockData);
  });
});
