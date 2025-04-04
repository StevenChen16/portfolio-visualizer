import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
import numpy as np

# 股票列表CSV文件路径
STOCKS_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'stocks.csv')

def search_stocks(query):
    """
    根据输入查询搜索匹配的股票
    
    Parameters:
    query (str): 搜索查询字符串
    
    Returns:
    list: 匹配的股票列表
    """
    try:
        # 检查文件是否存在，不存在则创建样例数据
        if not os.path.exists(STOCKS_CSV_PATH):
            # 创建一个样例股票列表CSV文件
            create_sample_stocks_csv()
        
        # 读取股票列表CSV
        stocks_df = pd.read_csv(STOCKS_CSV_PATH)
        
        # 搜索匹配项 (不区分大小写)
        query = query.lower()
        matches = stocks_df[
            stocks_df['symbol'].str.lower().str.contains(query) | 
            stocks_df['name'].str.lower().str.contains(query)
        ]
        
        # 转换为列表字典返回
        return matches.head(10).to_dict(orient='records')
    except Exception as e:
        print(f"搜索股票时出错: {e}")
        return []

def get_stock_data(symbol, start_date, end_date):
    """
    使用yfinance获取股票数据
    
    Parameters:
    symbol (str): 股票代码
    start_date (str): 开始日期 (YYYY-MM-DD)
    end_date (str): 结束日期 (YYYY-MM-DD)
    
    Returns:
    DataFrame: 股票历史数据
    """
    try:
        # 添加额外的天数以确保包含周末/假日
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=5)
        start_date_adj = start_datetime.strftime('%Y-%m-%d')
        
        # 获取股票数据
        stock_data = yf.download(symbol, start=start_date_adj, end=end_date, progress=False)
        
        # 确保日期列被设置为索引
        if not isinstance(stock_data.index, pd.DatetimeIndex):
            stock_data.set_index('Date', inplace=True)
        
        return stock_data
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        return pd.DataFrame()

def create_sample_stocks_csv():
    """创建样例股票列表CSV文件，用于测试"""
    sample_stocks = [
        {'symbol': 'AAPL', 'name': '苹果公司', 'sector': '技术'},
        {'symbol': 'MSFT', 'name': '微软公司', 'sector': '技术'},
        {'symbol': 'GOOGL', 'name': '谷歌公司', 'sector': '技术'},
        {'symbol': 'AMZN', 'name': '亚马逊公司', 'sector': '消费者服务'},
        {'symbol': 'TSLA', 'name': '特斯拉公司', 'sector': '汽车'},
        {'symbol': 'FB', 'name': '脸书公司', 'sector': '技术'},
        {'symbol': 'BABA', 'name': '阿里巴巴集团', 'sector': '零售业'},
        {'symbol': 'V', 'name': 'Visa Inc.', 'sector': '金融服务'},
        {'symbol': 'JD', 'name': '京东集团', 'sector': '零售业'},
        {'symbol': 'NTES', 'name': '网易公司', 'sector': '技术'},
        {'symbol': 'PDD', 'name': '拼多多', 'sector': '零售业'},
        {'symbol': '600519.SS', 'name': '贵州茅台', 'sector': '消费品'},
        {'symbol': '000858.SZ', 'name': '五粮液', 'sector': '消费品'},
        {'symbol': '601318.SS', 'name': '中国平安', 'sector': '金融服务'},
        {'symbol': '000001.SZ', 'name': '平安银行', 'sector': '金融服务'}
    ]
    
    # 创建DataFrame并保存为CSV
    df = pd.DataFrame(sample_stocks)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(STOCKS_CSV_PATH), exist_ok=True)
    
    # 保存CSV
    df.to_csv(STOCKS_CSV_PATH, index=False, encoding='utf-8')
    print(f"已创建样例股票列表: {STOCKS_CSV_PATH}")
