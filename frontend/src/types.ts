// 股票类型
export interface Stock {
  symbol: string;
  name: string;
  sector?: string;
}

// 股票交易类型
export interface StockTransaction {
  symbol: string;
  name: string;
  quantity: number;
  buy_date: string;
  buy_price: number;
}

// 投资组合数据类型
export interface PortfolioData {
  transactions: StockTransaction[];
  start_date?: string;
  end_date?: string;
}

// 投资组合价值数据点
export interface PortfolioValuePoint {
  Date: string;
  TotalValue: number;
  [key: string]: number | string;  // 每支股票的价值
}

// 指标类型
export interface Indicators {
  [key: string]: string | number | object;
}
