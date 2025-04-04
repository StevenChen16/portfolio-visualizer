import axios from 'axios';
import { Stock, StockTransaction, PortfolioData } from '../types';

// API 基础URL - 使用相对路径，CRA会通过proxy配置处理请求
const API_URL = '/api';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加响应拦截器，用于调试
api.interceptors.response.use(
  (response) => {
    console.log(`API响应成功 [${response.config.url}]:`, response.data);
    return response;
  },
  (error) => {
    console.error(`API响应错误 [${error.config?.url}]:`, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// 搜索股票
export const searchStocks = async (query: string): Promise<Stock[]> => {
  try {
    const response = await api.get(`/stocks/search?query=${encodeURIComponent(query)}`);
    return response.data.results;
  } catch (error) {
    console.error('搜索股票出错:', error);
    return [];
  }
};

// 获取特定日期的股票价格
export const getStockPrice = async (symbol: string, date: string): Promise<number | null> => {
  try {
    const response = await api.get(`/stock/price?symbol=${encodeURIComponent(symbol)}&date=${encodeURIComponent(date)}`);
    console.log('获取股票价格响应:', response.data);
    
    // 处理不同格式的价格响应
    if (response.data && response.data.price !== undefined) {
      // 如果价格是一个对象，例如: {AAPL: 162.125}
      if (typeof response.data.price === 'object' && response.data.price !== null) {
        // 尝试通过股票代码获取价格
        if (response.data.price[symbol] !== undefined) {
          return Number(response.data.price[symbol]);
        }
        // 或者取对象的第一个值
        const firstValue = Object.values(response.data.price)[0];
        if (firstValue !== undefined) {
          return Number(firstValue);
        }
      } 
      // 如果价格是一个直接值
      else if (typeof response.data.price === 'number' || typeof response.data.price === 'string') {
        return Number(response.data.price);
      }
    }
    console.warn('无法从响应中提取有效的价格数据:', response.data);
    return null;
  } catch (error) {
    console.error('获取股票价格出错:', error);
    return null;
  }
};

// 计算投资组合价值
export const calculatePortfolioValue = async (portfolioData: PortfolioData) => {
  try {
    console.log('发送请求到计算投资组合API:', portfolioData);
    const response = await api.post('/portfolio/value', portfolioData);
    console.log('计算投资组合API响应:', response.data);
    
    if (!response.data || !response.data.portfolio_value) {
      throw new Error('API响应格式不正确，缺少portfolio_value字段');
    }
    
    return {
      portfolioValue: response.data.portfolio_value,
      indicators: response.data.indicators || {}
    };
  } catch (error) {
    console.error('计算投资组合价值出错:', error);
    throw error;
  }
};
