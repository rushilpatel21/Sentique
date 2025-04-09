import {request} from "@/auth/allAuth.tsx";

const BASE_URL = '/api';

const URLs = {
    STATS: BASE_URL + '/stats/review-stats/',
    SENTIMENT_OVERVIEW: BASE_URL + '/stats/last-6-months/',
    TRENDING_TOPICS: BASE_URL + '/stats/trending-topics/',
    RECENT_FEEDBACK: BASE_URL + '/stats/recent-feedback/',
    FEEDBACK_SOURCES: BASE_URL + '/stats/feedback-sources/',
    SENTIMENT_DISTRIBUTION: BASE_URL + '/stats/sentiment-distribution/',
    SENTIMENT_TRENDS: BASE_URL + '/stats/sentiment-trends/',
    SENTIMENTS_BY_SOURCE: BASE_URL + '/stats/sentiments-by-source/',
    PRODUCT_FEEDBACK_CATEGORIES: BASE_URL + '/stats/product-feedback-categories/',
    FEATURE_SPECIFIC_FEEDBACK: BASE_URL + '/stats/feature-specific-feedback/',
    TOP_FEEDBACK_TOPICS: BASE_URL + '/stats/top-feedback-topics/',
    FEEDBACK_SOURCES_DEFAULT: BASE_URL + '/stats/feedback-detailed-sources/',
    FEEDBACK_DETAIL: BASE_URL + '/stats/feedback-detail/',
    GENERATE_REPORT: BASE_URL + '/reports/generate/',
}

export async function getStats(timeFilter): Promise<any> {
    return await request('GET', `${URLs.STATS}/${timeFilter}/`);
}

export async function getLast6Month(timeFilter): Promise<any> {
    return await request('GET', `${URLs.SENTIMENT_OVERVIEW}/default/`);
}

export async function getTrendingTopic(timeFilter): Promise<any> {
    return await request('GET', `${URLs.TRENDING_TOPICS}/default/`);
}

export async function getRecentFeedback(timeFilter): Promise<any> {
    return await request('GET', `${URLs.RECENT_FEEDBACK}/default/`);
}

export async function getFeedbackSources(timeFilter): Promise<any> {
    return await request('GET', `${URLs.FEEDBACK_SOURCES}${timeFilter}/`);
}

export async function getSentimentDistribution(): Promise<any> {
    return await request('GET', `${URLs.SENTIMENT_DISTRIBUTION}`);
}

export async function getSentimentTrends(): Promise<any> {
    return await request('GET', `${URLs.SENTIMENT_TRENDS}`);
}

export async function getSentimentBySource(): Promise<any> {
    return await request('GET', `${URLs.SENTIMENTS_BY_SOURCE}`);
}

export async function getProductFeedbackCategories(): Promise<any> {
    return await request('GET', `${URLs.PRODUCT_FEEDBACK_CATEGORIES}`);
}

export async function getFeatureSpecificFeedback(): Promise<any> {
    return await request('GET', `${URLs.FEATURE_SPECIFIC_FEEDBACK}`);
}

export async function getTopFeedbackTopics(): Promise<any> {
    return await request('GET', `${URLs.TOP_FEEDBACK_TOPICS}`);
}

export async function getFeedbackDetailedSources(): Promise<any> {
    return await request('GET', `${URLs.FEEDBACK_SOURCES_DEFAULT}`);
}

export async function getFeedbackDetails(searchTerm: string, source: string, sentiment: string, category: string, page:string): Promise<any> {
    return await request('GET', `${URLs.FEEDBACK_DETAIL}?search=${searchTerm}&source=${source}&sentiment=${sentiment}&category=${category}&page=${page}`);
}

// Helper function to get CSRF token from cookies
function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
}

/**
 * Formats a date into a readable string format
 * @param date The date to format
 * @returns Formatted date string (e.g. "April 6, 2025")
 */
function formatDateForDisplay(date) {
  if (!date) return '';
  
  // Format as "Month Day, Year"
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Generates a report by sending configuration to the backend API
 * @param config Report configuration parameters
 * @returns Promise with blob data for the generated report
 */
export const generateReport = async (config) => {
  try {
    // Format dates properly for better display
    const formatDate = (date) => {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    };

    // Create proper payload with correctly formatted dates
    const payload = {
      reportType: config.reportType,
      timeFilter: config.timeFilter,
      dateRange: {
        from: config.dateRange.from?.toISOString(),
        to: config.dateRange.to?.toISOString(),
        // These formatted dates will help the backend display them properly
        fromFormatted: formatDate(config.dateRange.from),
        toFormatted: formatDate(config.dateRange.to)
      },
      format: config.format,
      sections: config.sections
    };

    console.log('Sending report request with payload:', payload);

    const csrfToken = getCSRFToken();
    
    const response = await fetch('http://127.0.0.1:8000/reports/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken || '',
      },
      body: JSON.stringify(payload),
      credentials: 'include',
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage;
      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.error || errorData.detail || 'Failed to generate report';
      } catch {
        errorMessage = errorText || 'Failed to generate report';
      }
      throw new Error(errorMessage);
    }

    return await response.blob();
  } catch (error) {
    console.error('Error generating report:', error);
    throw error;
  }
};