import React, { useState, useEffect } from 'react';
import { Input, AutoComplete, DatePicker, InputNumber, Form, Button, Spin, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { searchStocks, getStockPrice } from '../services/api';
import { Stock, StockTransaction } from '../types';
import dayjs from 'dayjs';

interface StockSearchProps {
  onSelect: (transaction: StockTransaction) => void;
}

// 确保值是数字类型
const ensureNumber = (value: any): number => {
  if (value === null || value === undefined) return 0;
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  }
  return 0;
};

const StockSearch: React.FC<StockSearchProps> = ({ onSelect }) => {
  const [form] = Form.useForm();
  const [searchValue, setSearchValue] = useState<string>('');
  const [options, setOptions] = useState<{ value: string; label: React.ReactNode }[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [priceLoading, setPriceLoading] = useState<boolean>(false);

  // 搜索股票
  useEffect(() => {
    const fetchStocks = async () => {
      if (searchValue.length < 2) {
        setOptions([]);
        return;
      }

      setLoading(true);
      try {
        const results = await searchStocks(searchValue);
        
        const formattedOptions = results.map(stock => ({
          value: `${stock.symbol}-${stock.name}`,
          label: (
            <div className="stock-search-item">
              <span className="stock-symbol">{stock.symbol}</span>
              <span className="stock-name">{stock.name}</span>
            </div>
          ),
          stock
        }));
        
        setOptions(formattedOptions);
      } catch (error) {
        console.error('搜索股票时出错:', error);
        message.error('搜索股票时发生错误');
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchStocks, 300);
    return () => clearTimeout(timer);
  }, [searchValue]);

  // 当日期改变时获取股票价格
  const handleDateChange = async (date: dayjs.Dayjs | null) => {
    if (!date || !selectedStock) return;
    
    const dateStr = date.format('YYYY-MM-DD');
    setPriceLoading(true);
    
    try {
      const price = await getStockPrice(selectedStock.symbol, dateStr);
      if (price !== null) {
        // 确保价格是数字类型
        const numericPrice = ensureNumber(price);
        form.setFieldsValue({ buy_price: numericPrice });
      } else {
        message.warning('无法获取所选日期的股票价格');
      }
    } catch (error) {
      console.error('获取股票价格时出错:', error);
      message.error('获取股票价格时发生错误');
    } finally {
      setPriceLoading(false);
    }
  };

  // 处理股票选择
  const handleStockSelect = (value: string, option: any) => {
    setSelectedStock(option.stock);
    form.setFieldsValue({ symbol: option.stock.symbol, name: option.stock.name });
  };

  // 提交表单
  const handleSubmit = (values: any) => {
    if (!selectedStock) {
      message.error('请先选择一支股票');
      return;
    }

    const transaction: StockTransaction = {
      symbol: selectedStock.symbol,
      name: selectedStock.name,
      quantity: ensureNumber(values.quantity),
      buy_date: values.buy_date.format('YYYY-MM-DD'),
      buy_price: ensureNumber(values.buy_price)
    };

    console.log('添加交易，确保数字类型:', {
      原始价格: values.buy_price,
      处理后价格: transaction.buy_price,
      原始数量: values.quantity,
      处理后数量: transaction.quantity
    });

    onSelect(transaction);
    
    // 重置表单
    form.resetFields();
    setSelectedStock(null);
    setSearchValue('');
  };

  return (
    <Form form={form} layout="vertical" onFinish={handleSubmit}>
      <Form.Item name="stock_search" label="搜索股票" rules={[{ required: true, message: '请搜索并选择股票' }]}>
        <AutoComplete
          options={options}
          onSelect={handleStockSelect}
          onSearch={setSearchValue}
          value={searchValue}
          notFoundContent={loading ? <Spin size="small" /> : '未找到匹配的股票'}
          className="stock-search-dropdown"
        >
          <Input 
            placeholder="输入股票代码或名称..." 
            prefix={<SearchOutlined />} 
          />
        </AutoComplete>
      </Form.Item>

      <Form.Item name="symbol" hidden>
        <Input />
      </Form.Item>

      <Form.Item name="name" hidden>
        <Input />
      </Form.Item>

      <Form.Item name="buy_date" label="购买日期" rules={[{ required: true, message: '请选择购买日期' }]}>
        <DatePicker 
          style={{ width: '100%' }} 
          onChange={handleDateChange}
          placeholder="选择购买日期"
          disabled={!selectedStock}
        />
      </Form.Item>

      <Form.Item 
        name="buy_price" 
        label="购买价格" 
        rules={[{ required: true, message: '请输入购买价格' }]}
        extra={priceLoading ? <Spin size="small" /> : ''}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          min={0}
          precision={2}
          placeholder="输入购买价格"
          disabled={!selectedStock}
          // 确保输入的值始终为数字
          onChange={(value) => form.setFieldsValue({ buy_price: ensureNumber(value) })}
        />
      </Form.Item>

      <Form.Item 
        name="quantity" 
        label="购买数量" 
        rules={[{ required: true, message: '请输入购买数量' }]}
      >
        <InputNumber 
          style={{ width: '100%' }} 
          min={0}
          placeholder="输入购买数量"
          disabled={!selectedStock}
          // 确保输入的值始终为数字
          onChange={(value) => form.setFieldsValue({ quantity: ensureNumber(value) })}
        />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" disabled={!selectedStock}>
          添加到投资组合
        </Button>
      </Form.Item>
    </Form>
  );
};

export default StockSearch;
