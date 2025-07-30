import axios from 'axios';
import { getAuthToken } from './auth';

const request = axios.create({
  baseURL: process.env['API_BASE_URL'] || 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 处理认证失败的情况
      console.error('Authentication failed');
    }
    return Promise.reject(error);
  }
);

export { request }; 