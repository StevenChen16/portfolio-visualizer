from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import yfinance as yf
import os
import traceback
from datetime import datetime, timedelta
import uvicorn

from utils.data_fetcher import search_stocks, get_stock_data
from utils.indicators import calculate_portfolio_value, calculate_indicators

app = FastAPI(title="投资组合可视化系统", description="基于Python的投资组合分析后端")

# 配置CORS允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class StockTransaction(BaseModel):
    symbol: str
    name: str
    quantity: float
    buy_date: str  # ISO 格式日期字符串
    buy_price: float

class PortfolioData(BaseModel):
    transactions: List[StockTransaction]
    start_date: Optional[str] = None  # 不指定则使用最早交易日期
    end_date: Optional[str] = None  # 不指定则使用当前日期

# API端点
@app.get("/")
def read_root():
    return {"message": "投资组合可视化系统API已启动"}

@app.get("/api/stocks/search")
def api_search_stocks(query: str = Query(..., min_length=2)):
    """
    搜索股票，至少需要输入2个字符
    """
    try:
        results = search_stocks(query)
        return {"results": results}
    except Exception as e:
        print(f"搜索股票时出错: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/price")
def get_stock_price(symbol: str, date: str):
    """
    获取特定日期的股票价格，用于自动填充买入价格
    """
    try:
        print(f"获取股票价格: symbol={symbol}, date={date}")
        stock_data = get_stock_data(symbol, date, date)
        
        if stock_data.empty:
            print(f"没有找到股票 {symbol} 在 {date} 的价格数据")
            return {"price": None, "error": "没有该日期的价格数据"}
        
        price = stock_data["Close"].iloc[0]
        print(f"获取到价格: {price}, 类型: {type(price)}")
        return {"price": price}
    except Exception as e:
        print(f"获取股票价格时出错: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/value")
def calculate_portfolio_values(portfolio_data: PortfolioData):
    """
    计算投资组合在一段时间内的价值
    """
    try:
        print(f"收到计算投资组合请求, 交易数量: {len(portfolio_data.transactions)}")
        
        # 打印交易详情
        for i, tx in enumerate(portfolio_data.transactions):
            print(f"交易 {i+1}: symbol={tx.symbol}, name={tx.name}, quantity={tx.quantity}, buy_date={tx.buy_date}, buy_price={tx.buy_price}")
            
        # 如果没有指定开始日期，使用最早的交易日期
        if not portfolio_data.start_date:
            dates = [datetime.fromisoformat(tx.buy_date) for tx in portfolio_data.transactions]
            if not dates:
                raise ValueError("投资组合中没有交易")
            start_date = min(dates).strftime("%Y-%m-%d")
        else:
            start_date = portfolio_data.start_date
            
        # 如果没有指定结束日期，使用当前日期
        end_date = portfolio_data.end_date or datetime.now().strftime("%Y-%m-%d")
        
        print(f"计算日期范围: {start_date} 到 {end_date}")
        
        # 计算投资组合价值
        try:
            portfolio_value_df = calculate_portfolio_value(portfolio_data.transactions, start_date, end_date)
            print(f"计算投资组合价值成功, 数据点数量: {len(portfolio_value_df)}")
        except Exception as e:
            print(f"计算投资组合价值失败: {e}")
            print(traceback.format_exc())
            raise ValueError(f"计算投资组合价值失败: {e}")
        
        # 计算各种指标
        try:
            indicators = calculate_indicators(portfolio_value_df, portfolio_data.transactions)
            print(f"计算指标成功, 指标数量: {len(indicators)}")
        except Exception as e:
            print(f"计算指标失败: {e}")
            print(traceback.format_exc())
            indicators = {"计算错误": str(e)}
        
        result = {
            "portfolio_value": portfolio_value_df.to_dict(orient="records"),
            "indicators": indicators
        }
        
        print("计算投资组合完成")
        return result
    except Exception as e:
        error_msg = f"计算投资组合价值时出错: {e}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
