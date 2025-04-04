import React, { useState } from 'react';
import { Table, Button, Card, Spin, message, Empty, DatePicker } from 'antd';
import { DeleteOutlined, CalculatorOutlined } from '@ant-design/icons';
import { StockTransaction } from '../types';
import { calculatePortfolioValue } from '../services/api';
import dayjs from 'dayjs';

interface PortfolioTableProps {
  transactions: StockTransaction[];
  onRemove: (index: number) => void;
  onCalculate: (portfolioValue: any[], indicators: any) => void;
}

// 帮助函数：确保值是数字类型，用于安全调用toFixed
const ensureNumber = (value: any): number => {
  if (value === null || value === undefined) return 0;
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  }
  return 0;
};

const PortfolioTable: React.FC<PortfolioTableProps> = ({ 
  transactions, 
  onRemove,
  onCalculate
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [startDate, setStartDate] = useState<dayjs.Dayjs | null>(null);
  const [endDate, setEndDate] = useState<dayjs.Dayjs | null>(null);

  // 计算投资组合价值和指标
  const handleCalculate = async () => {
    if (transactions.length === 0) {
      message.warning('投资组合中没有股票，请先添加股票');
      return;
    }

    setLoading(true);
    try {
      console.log('准备计算投资组合，交易数据:', transactions);
      
      const portfolioData = {
        transactions,
        start_date: startDate ? startDate.format('YYYY-MM-DD') : undefined,
        end_date: endDate ? endDate.format('YYYY-MM-DD') : undefined,
      };

      console.log('发送到API的数据:', portfolioData);
      
      const result = await calculatePortfolioValue(portfolioData);
      console.log('API返回结果:', result);
      
      if (!result || !result.portfolioValue) {
        throw new Error('API返回的结果不包含投资组合价值数据');
      }
      
      onCalculate(result.portfolioValue, result.indicators || {});
      message.success('计算完成');
    } catch (error) {
      console.error('计算投资组合价值时出错:', error);
      // 显示更详细的错误信息
      if (error instanceof Error) {
        message.error(`计算投资组合时出错: ${error.message}`);
      } else {
        message.error('计算投资组合时出现未知错误');
      }
    } finally {
      setLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '购买日期',
      dataIndex: 'buy_date',
      key: 'buy_date',
    },
    {
      title: '购买价格',
      dataIndex: 'buy_price',
      key: 'buy_price',
      render: (price: any) => {
        const numPrice = ensureNumber(price);
        return `¥${numPrice.toFixed(2)}`;
      },
    },
    {
      title: '购买数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '总价值',
      key: 'total_value',
      render: (text: string, record: StockTransaction) => {
        const price = ensureNumber(record.buy_price);
        const quantity = ensureNumber(record.quantity);
        return `¥${(price * quantity).toFixed(2)}`;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (text: string, record: StockTransaction, index: number) => (
        <Button 
          icon={<DeleteOutlined />} 
          danger
          onClick={() => onRemove(index)}
        >
          删除
        </Button>
      ),
    },
  ];

  // 计算当前投资组合的总价值
  const totalValue = transactions.reduce(
    (sum, transaction) => {
      const price = ensureNumber(transaction.buy_price);
      const quantity = ensureNumber(transaction.quantity);
      return sum + price * quantity;
    },
    0
  );

  return (
    <Card 
      title="投资组合" 
      className="portfolio-card"
      extra={
        <div style={{ display: 'flex', gap: '8px' }}>
          <DatePicker 
            placeholder="开始日期（可选）" 
            onChange={setStartDate} 
            value={startDate}
          />
          <DatePicker 
            placeholder="结束日期（可选）" 
            onChange={setEndDate} 
            value={endDate}
          />
          <Button 
            type="primary" 
            icon={<CalculatorOutlined />} 
            onClick={handleCalculate}
            loading={loading}
          >
            计算投资组合
          </Button>
        </div>
      }
    >
      {transactions.length > 0 ? (
        <>
          <div style={{ marginBottom: '16px' }}>
            <strong>投资组合总价值: </strong>¥{totalValue.toFixed(2)}
          </div>
          <Table 
            columns={columns} 
            dataSource={transactions.map((tx, index) => ({ ...tx, key: index }))} 
            pagination={false}
            className="transaction-list"
            loading={loading}
          />
        </>
      ) : (
        <Empty description="暂无股票，请使用上方搜索栏添加股票" />
      )}
    </Card>
  );
};

export default PortfolioTable;
