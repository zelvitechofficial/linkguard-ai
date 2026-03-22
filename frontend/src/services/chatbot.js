import api from './api';

export const askChatbot = async (query) => {
  try {
    const response = await api.post('/chatbot/ask', { query });
    return response.data;
  } catch (error) {
    console.error('Chatbot API Error:', error);
    throw error;
  }
};

export const getTips = async (count) => {
  try {
    const response = await api.get('/chatbot/tips', { params: { count } });
    return response.data;
  } catch (error) {
    console.error('Chatbot Tips Error:', error);
    return { tips: [] };
  }
};

export const getTipOfTheDay = async () => {
  try {
    const response = await api.get('/chatbot/tip-of-the-day');
    return response.data;
  } catch (error) {
    console.error('Chatbot daily tip Error:', error);
    return { tip: 'Always check links before clicking!' };
  }
};

export const getFaqs = async () => {
  try {
    const response = await api.get('/chatbot/faqs');
    return response.data;
  } catch (error) {
    console.error('Chatbot FAQs Error:', error);
    return { faqs: [] };
  }
};

export default {
  askChatbot,
  getTips,
  getTipOfTheDay,
  getFaqs,
};
