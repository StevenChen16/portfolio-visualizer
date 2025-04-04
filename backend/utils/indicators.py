import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional

# 导入增强型指标模块
from .enhanced_indicators import (
    calculate_enhanced_indicators,
    calculate_win_loss_detailed_metrics,
    calculate_rolling_detailed_metrics,
    calculate_detailed_drawdown_metrics
)

def calculate_portfolio_value(transactions, start_date, end_date):
    """
    计算投资组合在指定时间段内的每日价值
    
    Parameters:
    transactions (List): 交易列表
    start_date (str): 开始日期
    end_date (str): 结束日期
    
    Returns:
    DataFrame: 包含日期和投资组合价值的DataFrame
    """
    try:
        # 获取日期范围
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # 创建结果DataFrame
        portfolio_value = pd.DataFrame(index=date_range)
        portfolio_value.index.name = 'Date'
        portfolio_value['TotalValue'] = 0.0
        
        # 为每个股票添加价值列
        symbols = set(tx.symbol for tx in transactions)
        for symbol in symbols:
            portfolio_value[symbol] = 0.0
        
        # 获取所有股票的历史数据
        stock_data = {}
        for symbol in symbols:
            try:
                print(f"下载 {symbol} 的历史数据...")
                data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if data.empty:
                    print(f"警告: 没有找到 {symbol} 的历史数据")
                stock_data[symbol] = data
            except Exception as e:
                print(f"获取 {symbol} 数据失败: {e}")
        
        # 计算每个交易在每一天的价值
        for tx in transactions:
            # 转换日期为datetime对象
            buy_date = datetime.fromisoformat(tx.buy_date)
            
            # 获取股票数据
            if tx.symbol not in stock_data or stock_data[tx.symbol].empty:
                print(f"跳过 {tx.symbol} 的价值计算，因为没有历史数据")
                continue
                
            stock_df = stock_data[tx.symbol]
            
            # 确保日期列是索引
            if not isinstance(stock_df.index, pd.DatetimeIndex):
                stock_df.set_index('Date', inplace=True)
            
            # 对于每一天，如果在买入日期之后，计算价值
            for date in portfolio_value.index:
                if date.date() >= buy_date.date():
                    # 找到最近的交易日
                    closest_date = find_closest_trading_date(stock_df, date)
                    if closest_date is not None:
                        price = stock_df.loc[closest_date, 'Close']
                        value = tx.quantity * price
                        
                        # 使用try-except块来安全更新DataFrame
                        try:
                            # 确保符号列存在
                            if tx.symbol not in portfolio_value.columns:
                                portfolio_value[tx.symbol] = 0.0
                                
                            # 使用更安全的方法更新值
                            current_value = portfolio_value.at[date, tx.symbol]
                            portfolio_value.at[date, tx.symbol] = current_value + value
                            
                            current_total = portfolio_value.at[date, 'TotalValue']
                            portfolio_value.at[date, 'TotalValue'] = current_total + value
                        except Exception as e:
                            print(f"更新 {tx.symbol} 在 {date} 的价值时出错: {e}")
                            print(f"当前行索引类型: {type(date)}, 当前列索引: {portfolio_value.columns.tolist()}")
                            # 确保不会中断整个计算过程
                            continue
        
        # 填充缺失值
        portfolio_value.fillna(0, inplace=True)
        
        # 重置索引使Date成为列
        portfolio_value = portfolio_value.reset_index()
        
        # 确保日期是字符串格式
        portfolio_value['Date'] = portfolio_value['Date'].dt.strftime('%Y-%m-%d')
        
        return portfolio_value
    except Exception as e:
        print(f"计算投资组合价值时出现错误: {e}")
        # 返回一个最小的有效DataFrame而不是抛出异常
        result = pd.DataFrame({'Date': [start_date], 'TotalValue': [0.0]})
        for symbol in set(tx.symbol for tx in transactions):
            result[symbol] = 0.0
        return result

def find_closest_trading_date(stock_df, date):
    """
    找到最近的交易日期
    
    Parameters:
    stock_df (DataFrame): 股票数据
    date (datetime): 目标日期
    
    Returns:
    datetime or None: 最近的交易日期或None
    """
    try:
        # 获取小于等于目标日期的最近交易日
        available_dates = stock_df.index[stock_df.index <= date]
        if not available_dates.empty:
            return available_dates[-1]
    except Exception as e:
        print(f"查找交易日期时出错: {e}")
    return None

def calculate_indicators(portfolio_value_df, transactions):
    """
    计算投资组合指标
    
    Parameters:
    portfolio_value_df (DataFrame): 投资组合价值数据
    transactions (List): 交易列表
    
    Returns:
    Dict: 计算的指标 - 包含丰富的投资指标信息
    """
    indicators = {}
    
    # 打印数据结构以便调试
    print(f"计算指标 - 数据点数量: {len(portfolio_value_df)}")
    print(f"计算指标 - 列: {portfolio_value_df.columns.tolist()}")
    print(f"计算指标 - 交易数量: {len(transactions)}")
    
    # 确保有足够的数据点
    if len(portfolio_value_df) < 2:
        print("警告: 数据点不足，无法计算有意义的指标")
        return {"信息": "数据点不足，无法计算有意义的指标"}
    
    # 提取总价值列
    total_values = portfolio_value_df['TotalValue'].values
    print(f"总价值数组: {total_values}")
    
    # 确保日期列是有效的
    if 'Date' in portfolio_value_df.columns:
        dates = pd.to_datetime(portfolio_value_df['Date'])
        # 使用.iloc来安全地访问第一个和最后一个元素，而不是使用负索引
        first_date = dates.iloc[0]
        last_date = dates.iloc[len(dates) - 1]
        print(f"日期范围: {first_date} 到 {last_date}")
    else:
        print("警告: 没有找到Date列，使用默认日期范围")
        # 创建一个默认的日期范围
        start_date = pd.Timestamp('2020-01-01')
        end_date = pd.Timestamp('2020-01-01') + pd.Timedelta(days=len(portfolio_value_df) - 1)
        first_date = start_date
        last_date = end_date
        dates = pd.date_range(start=start_date, end=end_date, periods=len(portfolio_value_df))
    
    # 计算初始投资
    initial_investment = sum(tx.quantity * tx.buy_price for tx in transactions)
    print(f"初始投资: {initial_investment}")
    if initial_investment <= 0:
        print("警告: 初始投资为零或负值")
        initial_investment = 1.0  # 防止除以零错误
    
    # 计算最终投资组合价值
    if len(total_values) > 0:
        final_value = total_values[-1]  # 这里使用-1是安全的，因为是numpy数组
        print(f"最终价值: {final_value}")
        if final_value < 0:
            print("警告: 最终价值为负")
            final_value = 0.0
    else:
        print("警告: 总价值数组为空")
        final_value = 0.0
    
    # 计算每日价值和变化率
    if len(portfolio_value_df) > 1:
        daily_values = portfolio_value_df['TotalValue'].values
        # 确保没有零值或负值导致无法计算
        valid_indices = np.where(daily_values[:-1] > 0)[0]
        if len(valid_indices) > 0:
            valid_values_prev = daily_values[valid_indices]
            valid_values_next = daily_values[valid_indices + 1]
            daily_returns = (valid_values_next - valid_values_prev) / valid_values_prev
        else:
            daily_returns = np.array([])
            print("警告: 没有足够的有效价值来计算每日回报率")
    else:
        daily_returns = np.array([])
        print("警告: 没有足够的数据点来计算每日回报率")
    
    # 1. 收益指标
    # 总收益率
    if initial_investment > 0:
        total_return = (final_value - initial_investment) / initial_investment * 100
        indicators['总收益率'] = f"{total_return:.2f}%"
        print(f"总收益率: {total_return:.2f}%")
    else:
        indicators['总收益率'] = "N/A (初始投资为零)"
        print("警告: 无法计算总收益率，初始投资为零")
    
    # 年化收益率和CAGR
    # 使用日期对象计算天数，而不是使用索引
    days = (last_date - first_date).days
    print(f"投资天数: {days} (从 {first_date} 到 {last_date})")
    
    if days > 0 and initial_investment > 0 and final_value > 0:
        years = days / 365.0
        # 避免负数导致的复数结果
        if final_value > initial_investment:
            annualized_return = ((final_value / initial_investment) ** (1 / years) - 1) * 100
            indicators['年化收益率'] = f"{annualized_return:.2f}%"
            print(f"年化收益率计算: (({final_value} / {initial_investment}) ** (1 / {years}) - 1) * 100 = {annualized_return:.2f}%")
        else:
            # 负收益，使用简单年化计算
            annualized_return = ((final_value - initial_investment) / initial_investment) * (365.0 / days) * 100
            indicators['年化收益率'] = f"{annualized_return:.2f}%"
            print(f"负收益年化计算: (({final_value} - {initial_investment}) / {initial_investment}) * (365 / {days}) * 100 = {annualized_return:.2f}%")
    else:
        indicators['年化收益率'] = "N/A"
        annualized_return = 0
        print(f"警告: 无法计算年化收益率，投资天数: {days}, 初始投资: {initial_investment}, 最终价值: {final_value}")
    
    # 2. 风险指标
    if len(daily_returns) > 0:
        # 波动率 (标准差)
        volatility = np.std(daily_returns) * np.sqrt(252) * 100  # 年化
        indicators['波动率(年化)'] = f"{volatility:.2f}%"
        
        # 最大回撤
        max_drawdown = calculate_max_drawdown(total_values) * 100
        indicators['最大回撤'] = f"{max_drawdown:.2f}%"
        
        # 增强型指标 - 使用新创建的模块来扩展指标系统
        print("计算增强型指标...")
        
        # 1. 计算高级指标
        enhanced_metrics = calculate_enhanced_indicators(
            portfolio_value_df=portfolio_value_df,
            daily_returns=daily_returns,
            total_values=total_values,
            initial_investment=initial_investment,
            final_value=final_value,
            first_date=first_date,
            last_date=last_date,
            transactions=transactions
        )
        
        # 将增强型指标整合到主指标字典中
        for key, value in enhanced_metrics.items():
            if key not in indicators:
                indicators[key] = value
                print(f"添加增强型指标: {key}")
        
        # 2. 计算详细的胜率/赔率分析
        if len(daily_returns) > 10:  # 至少需要10天的数据
            win_loss_detailed = calculate_win_loss_detailed_metrics(daily_returns)
            indicators['胜负详细分析'] = win_loss_detailed
            print("添加胜负详细分析")
        
        # 3. 计算滚动指标（如果有足够数据）
        if len(daily_returns) >= 60:  # 至少需要60天数据
            # 20日滚动指标
            rolling_20_detailed = calculate_rolling_detailed_metrics(daily_returns, window=20)
            indicators['20日滚动分析'] = rolling_20_detailed
            
            # 60日滚动指标
            rolling_60_detailed = calculate_rolling_detailed_metrics(daily_returns, window=60)
            indicators['60日滚动分析'] = rolling_60_detailed
            print("添加滚动指标分析")
        
        # 4. 计算回撤相关详细指标
        if len(total_values) > 30:
            drawdown_detailed = calculate_detailed_drawdown_metrics(total_values, portfolio_value_df['Date'].tolist())
            indicators['回撤详细分析'] = drawdown_detailed
            print("添加回撤详细分析")
        
        # 夏普比率 (假设无风险利率为2%)
        risk_free_rate = 0.02
        daily_std = np.std(daily_returns)
        if daily_std > 0:
            sharpe_ratio = ((np.mean(daily_returns) * 252) - risk_free_rate) / (daily_std * np.sqrt(252))
            indicators['夏普比率'] = f"{sharpe_ratio:.2f}"
        else:
            indicators['夏普比率'] = "N/A (无波动性)"
        
        # 收益风险比
        if max_drawdown > 0:
            risk_return_ratio = abs(total_return / max_drawdown)
            indicators['收益风险比'] = f"{risk_return_ratio:.2f}"
        else:
            indicators['收益风险比'] = "N/A (无回撤)"
            
        # 下行风险
        negative_returns = daily_returns[daily_returns < 0]
        if len(negative_returns) > 0:
            downside_risk = np.std(negative_returns) * np.sqrt(252) * 100
            indicators['下行风险'] = f"{downside_risk:.2f}%"
        else:
            indicators['下行风险'] = "0.00%"
        
        # 索提诺比率 (下行风险替代标准差)
        if len(negative_returns) > 0 and np.std(negative_returns) > 0:
            sortino_ratio = ((np.mean(daily_returns) * 252) - risk_free_rate) / (np.std(negative_returns) * np.sqrt(252))
            indicators['索提诺比率'] = f"{sortino_ratio:.2f}"
        else:
            indicators['索提诺比率'] = "N/A (无下行风险)"
        
        # 最大连续上涨/下跌天数
        if len(daily_returns) > 0:
            up_days = np.where(daily_returns > 0, 1, 0)
            down_days = np.where(daily_returns < 0, 1, 0)
            
            max_up_streak = calculate_max_streak(up_days)
            max_down_streak = calculate_max_streak(down_days)
            
            indicators['最大连续上涨天数'] = f"{max_up_streak}天"
            indicators['最大连续下跌天数'] = f"{max_down_streak}天"
        
        # 胜率 (正收益天数比例)
        if len(daily_returns) > 0:
            win_rate = np.sum(daily_returns > 0) / len(daily_returns) * 100
            indicators['胜率'] = f"{win_rate:.2f}%"
            
        # 平均每日收益
        if len(daily_returns) > 0:
            avg_daily_return = np.mean(daily_returns) * 100
            indicators['平均每日收益'] = f"{avg_daily_return:.4f}%"
            
        # 新增: 卡尔玛比率 (年化收益率/最大回撤)
        if max_drawdown > 0 and annualized_return != 0:
            calmar_ratio = abs(annualized_return / max_drawdown)
            indicators['卡尔玛比率'] = f"{calmar_ratio:.2f}"
        else:
            indicators['卡尔玛比率'] = "N/A"
            
        # 新增: 胜率/败率分析
        win_loss_metrics = calculate_win_loss_metrics(daily_returns)
        indicators.update(win_loss_metrics)
        
        # 新增: 滚动波动率分析 (20天和60天)
        if len(daily_returns) >= 20:
            rolling_20d = calculate_rolling_metrics(daily_returns, window=20)
            indicators.update(rolling_20d)
            
        if len(daily_returns) >= 60:
            rolling_60d = calculate_rolling_metrics(daily_returns, window=60)
            indicators.update(rolling_60d)
            
        # 新增: 详细回撤分析
        # 只有当有足够的数据点且日期数据可用时才计算
        if len(total_values) > 20 and len(dates) == len(total_values):
            # 将日期转换为列表，以便通过索引访问
            date_list = dates.tolist()
            drawdown_metrics = calculate_drawdown_metrics(total_values, date_list)
            indicators.update(drawdown_metrics)
    else:
        indicators['波动率(年化)'] = "N/A"
        indicators['最大回撤'] = "N/A"
        indicators['夏普比率'] = "N/A"
        indicators['收益风险比'] = "N/A"
        indicators['下行风险'] = "N/A"
        indicators['索提诺比率'] = "N/A"
        indicators['最大连续上涨天数'] = "N/A"
        indicators['最大连续下跌天数'] = "N/A"
        indicators['胜率'] = "N/A"
        indicators['平均每日收益'] = "N/A"
        indicators['卡尔玛比率'] = "N/A"
        print("警告: 无法计算风险指标，没有有效的每日回报率")
    
    # 3. 投资组合分析
    # 计算每个股票的权重
    latest_values = {}
    for symbol in portfolio_value_df.columns:
        if symbol not in ['Date', 'TotalValue'] and symbol in portfolio_value_df.columns:
            try:
                latest_values[symbol] = float(portfolio_value_df[symbol].iloc[-1])
            except Exception as e:
                print(f"获取 {symbol} 最新价值时出错: {e}")
                latest_values[symbol] = 0.0
    
    print(f"各股票最新价值: {latest_values}")
    
    if final_value > 0 and latest_values:
        weights = {symbol: (value / final_value * 100) for symbol, value in latest_values.items()}
        indicators['股票权重'] = {symbol: f"{weight:.2f}%" for symbol, weight in weights.items()}
        
        # 计算基尼系数，衡量投资集中度或多样性
        if len(weights) > 1:
            gini_coefficient = calculate_gini_coefficient(list(weights.values()))
            indicators['投资集中度(基尼系数)'] = f"{gini_coefficient:.2f}"
            
            # 基于香农熵的多样性指标
            diversity_score = calculate_diversity_score(list(weights.values()))
            indicators['投资多样性(熵值)'] = f"{diversity_score:.2f}"
        else:
            indicators['投资集中度(基尼系数)'] = "1.00 (单一投资)"
            indicators['投资多样性(熵值)'] = "0.00 (单一投资)"
        
        # 获取最大贡献股票
        if weights:
            max_contributor = max(weights.items(), key=lambda x: x[1])
            indicators['最大贡献'] = f"{max_contributor[0]}: {max_contributor[1]:.2f}%"
            print(f"最大贡献: {indicators['最大贡献']}")
        else:
            indicators['最大贡献'] = "无"
            print("警告: 没有权重信息")
    else:
        indicators['股票权重'] = {symbol: "0.00%" for symbol in latest_values.keys()}
        indicators['最大贡献'] = "无 (投资组合价值为0)"
        indicators['投资集中度(基尼系数)'] = "N/A"
        indicators['投资多样性(熵值)'] = "N/A"
        print("警告: 最终价值为零或没有股票价值")
    
    return indicators


def calculate_max_drawdown(values):
    """
    计算最大回撤
    
    Parameters:
    values (array): 投资组合价值数组
    
    Returns:
    float: 最大回撤比例
    """
    if len(values) < 2:
        print("警告: 数据点不足，无法计算最大回撤")
        return 0.0
        
    max_so_far = values[0]
    max_drawdown = 0.0
    
    for value in values:
        if value > max_so_far:
            max_so_far = value
        
        # 防止除以零
        if max_so_far > 0:
            drawdown = (max_so_far - value) / max_so_far
            max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown


def calculate_max_streak(binary_array):
    """
    计算最大连续1的天数
    
    Parameters:
    binary_array (array): 二进制数组，1表示上涨/下跌，0表示其他
    
    Returns:
    int: 最大连续天数
    """
    max_streak = 0
    current_streak = 0
    
    for value in binary_array:
        if value == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
            
    return max_streak


def calculate_gini_coefficient(weights):
    """
    计算基尼系数，衡量投资集中度
    系数接近1表示非常集中，接近0表示非常分散
    
    Parameters:
    weights (list): 权重列表
    
    Returns:
    float: 基尼系数
    """
    # 标准化权重
    weights = np.array(weights) / 100.0
    weights = np.sort(weights)
    n = len(weights)
    
    if n <= 1:
        return 1.0
    
    # 计算洛伦兹曲线下方的面积
    lorentz_curve_area = np.sum([(i+1) * weight for i, weight in enumerate(weights)]) / (n * np.sum(weights))
    
    # 基尼系数 = 1 - 2 * 洛伦兹曲线下方面积
    gini = 1 - 2 * lorentz_curve_area
    
    return gini


def calculate_diversity_score(weights):
    """
    基于香农熵计算投资多样性得分
    得分越高表示投资越分散
    
    Parameters:
    weights (list): 权重列表
    
    Returns:
    float: 多样性得分
    """
    # 标准化权重
    weights = np.array(weights) / 100.0
    
    # 过滤掉零权重
    weights = weights[weights > 0]
    
    if len(weights) <= 1:
        return 0.0
    
    # 计算香农熵
    entropy = -np.sum(weights * np.log(weights))
    
    # 最大可能熵 (当所有权重相等时)
    max_entropy = np.log(len(weights))
    
    # 归一化熵值
    if max_entropy > 0:
        diversity = entropy / max_entropy
    else:
        diversity = 0.0
        
    return diversity


def calculate_win_loss_metrics(daily_returns):
    """
    计算胜率和赔率相关指标
    
    Parameters:
    daily_returns (array): 日收益率数组
    
    Returns:
    dict: 胜率和赔率相关指标
    """
    result = {}
    
    # 区分正收益和负收益
    positive_returns = daily_returns[daily_returns > 0]
    negative_returns = daily_returns[daily_returns < 0]
    
    # 计算胜率
    win_rate = len(positive_returns) / len(daily_returns) * 100
    result['详细胜率'] = f"{win_rate:.2f}%"
    
    # 平均收益和损失
    if len(positive_returns) > 0:
        avg_gain = np.mean(positive_returns) * 100
        result['平均收益(盈利日)'] = f"{avg_gain:.4f}%"
    else:
        avg_gain = 0
        result['平均收益(盈利日)'] = "N/A"
    
    if len(negative_returns) > 0:
        avg_loss = np.mean(negative_returns) * 100
        result['平均损失(亏损日)'] = f"{avg_loss:.4f}%"
    else:
        avg_loss = 0
        result['平均损失(亏损日)'] = "N/A"
    
    # 收益/损失比率 (赔率)
    if avg_loss != 0:
        gain_loss_ratio = abs(avg_gain / avg_loss)
        result['收益/损失比'] = f"{gain_loss_ratio:.2f}"
    else:
        result['收益/损失比'] = "N/A (无损失)"
    
    # 期望值
    expectancy = (win_rate/100 * avg_gain/100) + ((1-win_rate/100) * avg_loss/100)
    result['每日期望收益'] = f"{expectancy*100:.4f}%"
    
    return result


def calculate_rolling_metrics(daily_returns, window=20):
    """
    计算滚动指标
    
    Parameters:
    daily_returns (array): 日收益率数组
    window (int): 滚动窗口大小
    
    Returns:
    dict: 滚动指标
    """
    result = {}
    
    # 使用pandas的rolling函数
    returns_series = pd.Series(daily_returns)
    
    if len(returns_series) < window:
        result[f"{window}日滚动分析"] = "数据点不足"
        return result
    
    rolling_mean = returns_series.rolling(window=window).mean()
    rolling_std = returns_series.rolling(window=window).std()
    
    # 最新的滚动指标
    latest_rolling_return = rolling_mean.iloc[-1] * 252 * 100  # 年化
    latest_rolling_volatility = rolling_std.iloc[-1] * np.sqrt(252) * 100  # 年化
    
    result[f"{window}日滚动年化收益"] = f"{latest_rolling_return:.2f}%"
    result[f"{window}日滚动年化波动率"] = f"{latest_rolling_volatility:.2f}%"
    
    # 最高和最低的滚动波动率
    max_volatility_idx = rolling_std.idxmax()
    min_volatility_idx = rolling_std[rolling_std > 0].idxmin()
    
    if not pd.isna(max_volatility_idx):
        max_volatility = rolling_std.loc[max_volatility_idx] * np.sqrt(252) * 100
        result[f"{window}日最高历史波动率"] = f"{max_volatility:.2f}%"
    
    if not pd.isna(min_volatility_idx):
        min_volatility = rolling_std.loc[min_volatility_idx] * np.sqrt(252) * 100
        result[f"{window}日最低历史波动率"] = f"{min_volatility:.2f}%"
    
    return result


def calculate_drawdown_metrics(portfolio_values, dates):
    """
    计算回撤相关指标
    
    Parameters:
    portfolio_values (array): 投资组合价值数组
    dates (list): 对应的日期列表
    
    Returns:
    dict: 回撤相关指标
    """
    result = {}
    
    if len(portfolio_values) < 5:
        result['回撤分析'] = "数据点不足"
        return result
    
    # 初始化
    peak_value = portfolio_values[0]
    peak_idx = 0
    drawdown_start_idx = 0
    drawdown_end_idx = 0
    current_drawdown = 0
    max_drawdown = 0
    max_drawdown_start_idx = 0
    max_drawdown_end_idx = 0
    
    # 计算每个时间点的回撤
    drawdowns = []
    for i, value in enumerate(portfolio_values):
        # 更新峰值
        if value > peak_value:
            peak_value = value
            peak_idx = i
        
        # 计算当前回撤
        if peak_value > 0:
            current_drawdown = (peak_value - value) / peak_value
        else:
            current_drawdown = 0
        
        drawdowns.append(current_drawdown)
        
        # 检查是否为新的最大回撤
        if current_drawdown > max_drawdown:
            max_drawdown = current_drawdown
            max_drawdown_start_idx = peak_idx
            max_drawdown_end_idx = i
    
    # 如果有最大回撤，添加详细信息
    if max_drawdown > 0 and max_drawdown_start_idx < len(dates) and max_drawdown_end_idx < len(dates):
        max_dd_start_date = dates[max_drawdown_start_idx]
        max_dd_end_date = dates[max_drawdown_end_idx]
        
        # 计算回撤持续时间 - 修复datetime类型检查
        if isinstance(max_dd_start_date, (pd.Timestamp, datetime)) and isinstance(max_dd_end_date, (pd.Timestamp, datetime)):
            dd_duration = (max_dd_end_date - max_dd_start_date).days
            
            result['最大回撤开始日期'] = max_dd_start_date.strftime('%Y-%m-%d')
            result['最大回撤结束日期'] = max_dd_end_date.strftime('%Y-%m-%d')
            result['最大回撤持续时间'] = f"{dd_duration}天"
            
            # 计算恢复期 (如果有)
            recovery_idx = None
            for i in range(max_drawdown_end_idx + 1, len(portfolio_values)):
                if portfolio_values[i] >= portfolio_values[max_drawdown_start_idx]:
                    recovery_idx = i
                    break
            
            if recovery_idx and recovery_idx < len(dates):
                recovery_date = dates[recovery_idx]
                if isinstance(recovery_date, (pd.Timestamp, datetime)):
                    recovery_duration = (recovery_date - max_dd_end_date).days
                    total_cycle = dd_duration + recovery_duration
                    
                    result['回撤恢复日期'] = recovery_date.strftime('%Y-%m-%d')
                    result['回撤恢复时间'] = f"{recovery_duration}天"
                    result['完整回撤周期'] = f"{total_cycle}天"
                else:
                    result['回撤恢复'] = "尚未恢复到峰值"
            else:
                result['回撤恢复'] = "尚未恢复到峰值"
    
    # 计算平均回撤和回撤频率
    if drawdowns:
        avg_drawdown = np.mean(drawdowns) * 100
        result['平均回撤'] = f"{avg_drawdown:.2f}%"
        
        # 计算有意义的回撤次数 (超过2%的回撤)
        significant_drawdowns = sum(1 for dd in drawdowns if dd > 0.02)
        result['显著回撤次数(>2%)'] = str(significant_drawdowns)
        
        if len(dates) > 1:
            # 估计年化回撤频率
            first_date = dates[0]
            last_date = dates[-1]
            if isinstance(first_date, (pd.Timestamp, datetime)) and isinstance(last_date, (pd.Timestamp, datetime)):
                years = (last_date - first_date).days / 365.0
                if years > 0:
                    annual_dd_freq = significant_drawdowns / years
                    result['年化显著回撤频率'] = f"{annual_dd_freq:.2f}次/年"
    
    return result
