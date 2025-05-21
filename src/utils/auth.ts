import axios from 'axios';
import qs from 'qs';

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
}

const AUTH_CONFIG = {
  baseURL: 'https://aevatar-station-ui-staging.aevatar.ai',
  clientId: 'AevatarAuthServer',
  scope: 'Aevatar offline_access',
};

export const getToken = async (username: string, password: string): Promise<TokenResponse> => {
  try {
    const response = await axios.post(
      '/connect/token',
      qs.stringify({
        grant_type: 'password',
        scope: AUTH_CONFIG.scope,
        username,
        password,
        client_id: AUTH_CONFIG.clientId,
      }),
      {
        baseURL: AUTH_CONFIG.baseURL,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': '*/*',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
        },
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to get token: ${error.response?.data?.error_description || error.message}`);
    }
    throw error;
  }
};

export const setAuthToken = (token: string) => {
  localStorage.setItem('auth_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const removeAuthToken = () => {
  localStorage.removeItem('auth_token');
}; 