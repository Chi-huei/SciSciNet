import axios from 'axios';

const API_BASE_URL = '/api';

export interface ChatResponse {
  text: string;
  vega_spec: any;
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await axios.post(`${API_BASE_URL}/chat`, {
    message,
  });

  return response.data;
}
