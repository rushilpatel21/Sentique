import axios from 'axios';
import { DateRange } from 'react-day-picker';

// Set the base URL for API requests
const API_URL = 'http://localhost:8000/api';

// Interface for analysis results
interface AnalysisResult {
  positiveInsights: string[];
  negativeInsights: string[];
  summary: string;
  metadata?: {
    reviewCount: number;
    dateRange: {
      from: string;
      to: string;
    };
    category: string;
  };
  error?: string;
}

// Function to generate trend analysis
export const generateTrendAnalysis = async (
  category: string,
  dateRange: DateRange,
  timePreset?: string
): Promise<AnalysisResult> => {
  try {
    const requestData: any = { category };
    
    if (timePreset) {
      // If a preset is provided, use that
      requestData.timePreset = timePreset;
    } else {
      // Otherwise use the date range
      requestData.dateRange = {
        from: dateRange.from?.toISOString().split('T')[0],
        to: dateRange.to?.toISOString().split('T')[0],
      };
    }
    
    const response = await axios.post(`${API_URL}/trends/analysis/`, requestData);
    
    return response.data;
  } catch (error) {
    console.error('Error generating trend analysis:', error);
    throw error;
  }
};