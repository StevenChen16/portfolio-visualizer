import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def calculate_enhanced_indicators(portfolio_value_df, daily_returns, total_values, initial_investment, final_value, first_date, last_date, transactions):
    """
    计算增强型投资组合指标
    
    Parameters:
    portfolio_value_df (DataFrame): 投资组合价值数据
    daily_returns (array): 日收益率数组
    total_values (array): 总价值数组
    initial_investment (float): 初始投资金额
    final_value (float): 最终投资组合价值
    first_date (datetime): 开始日期
    last_date (datetime): 结束日期
    transactions (List): 交易列表
    
    Returns:
    Dict: 计算的指标
    """
    enhanced_indicators = {}
    
    # 计算总回报率
    total_return = (final_value - initial_investment) / initial_investment if initial_investment > 0 else 0
    
    # 计算投资时间（年）
    time_diff = (last_date - first_date).days / 365.25
    
    # 计算年化收益率
    if time_diff > 0.01 and initial_investment > 0 and final_value > 0:
        # 避免负数导致的复数结果
        if final_value > initial_investment:
            annualized_return = (1 + total_return) ** (1 / time_diff) - 1
        else:
            # 负收益，使用简单年化计算
            annualized_return = ((final_value - initial_investment) / initial_investment) * (365.0 / (last_date - first_date).days)
    else:
        annualized_return = 0
    
    ### 1. 收益性指标 ###
    
    # ROI (投资回报率)
    enhanced_indicators['ROI'] = f"{total_return * 100:.2f}%"
    
    # 绝对收益
    absolute_return = final_value - initial_investment
    enhanced_indicators['绝对收益'] = f"{absolute_return:.2f}"
    
    # 时间加权收益率 (TWR)
    if len(daily_returns) > 0:
        twr = np.prod(1 + daily_returns) - 1
        enhanced_indicators['时间加权收益率'] = f"{twr * 100:.2f}%"
    else:
        enhanced_indicators['时间加权收益率'] = "N/A"
    
    # 资金加权收益率 (IRR) - 简化处理
    if len(transactions) == 1:
        enhanced_indicators['资金加权收益率'] = f"{annualized_return * 100:.2f}%"
    else:
        enhanced_indicators['资金加权收益率'] = "需要详细现金流数据"
    
    ### 2. 风险评估指标 ###
    
    if len(daily_returns) > 0:
        # 日波动率
        daily_volatility = np.std(daily_returns)
        enhanced_indicators['日波动率'] = f"{daily_volatility * 100:.4f}%"
        
        # 年化波动率（假设252个交易日）
        annualized_volatility = daily_volatility * np.sqrt(252)
        enhanced_indicators['年化波动率'] = f"{annualized_volatility * 100:.2f}%"
        
        # 无风险利率 (假设为2%)
        risk_free_rate = 0.02
        daily_risk_free = risk_free_rate / 252  # 日无风险收益率
        
        # 索提诺比率 (仅考虑下行波动率)
        downside_returns = daily_returns[daily_returns < daily_risk_free]
        if len(downside_returns) > 0:
            downside_deviation = np.std(downside_returns) * np.sqrt(252)
            sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            enhanced_indicators['索提诺比率'] = f"{sortino_ratio:.2f}"
        else:
            enhanced_indicators['索提诺比率'] = "无下行波动"
        
        # 特雷诺比率 - 假设贝塔值为1.0，需要市场数据才能准确计算
        beta = 1.0
        treynor_ratio = (annualized_return - risk_free_rate) / beta if beta > 0 else 0
        enhanced_indicators['特雷诺比率'] = f"{treynor_ratio:.2f}"
        
        # 风险值(VaR) - 95%置信度下的VaR
        var_95 = np.percentile(daily_returns, 5) * np.sqrt(1)  # 1天VaR
        enhanced_indicators['风险值(VaR 95%)'] = f"{var_95 * 100:.2f}%"
        
        # 条件风险值(CVaR/Expected Shortfall)
        cvar_95 = np.mean(daily_returns[daily_returns <= var_95])
        enhanced_indicators['条件风险值(CVaR 95%)'] = f"{cvar_95 * 100:.2f}%"
        
        # 下行偏差
        target_return = 0  # 目标收益率，可以是0或无风险收益率
        downside_dev = np.sqrt(np.mean(np.minimum(daily_returns - target_return, 0) ** 2)) * np.sqrt(252)
        enhanced_indicators['下行偏差'] = f"{downside_dev * 100:.2f}%"
        
        # 阿尔法 - 需要市场基准，简化计算
        # 假设市场平均年收益率为8%
        market_return = 0.08
        alpha = annualized_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        enhanced_indicators['阿尔法'] = f"{alpha * 100:.2f}%"
        
        # 信息比率 - 需要基准，简化计算
        # 假设跟踪误差为5%
        tracking_error = 0.05
        information_ratio = (annualized_return - market_return) / tracking_error
        enhanced_indicators['信息比率'] = f"{information_ratio:.2f}"
    
    ### 3. 多元化与资产配置指标 ###
    
    # 获取每个股票的权重
    symbol_values = {}
    for symbol in set(tx.symbol for tx in transactions):
        if symbol in portfolio_value_df.columns:
            symbol_values[symbol] = portfolio_value_df[symbol].iloc[-1]
    
    total_portfolio_value = sum(symbol_values.values())
    if total_portfolio_value > 0:
        # 计算股票权重
        weights = {symbol: value / total_portfolio_value * 100 for symbol, value in symbol_values.items()}
        enhanced_indicators['股票权重'] = {symbol: f"{weight:.2f}%" for symbol, weight in weights.items()}
        
        numeric_weights = list(weights.values())
        
        # 权重集中度 (赫芬达尔指数)
        if len(numeric_weights) > 0:
            hhi = sum([w ** 2 for w in [v/100 for v in numeric_weights]])
            enhanced_indicators['权重集中度(HHI)'] = f"{hhi:.2f}"
        
        # 基尼系数 - 衡量投资集中度
        if len(numeric_weights) > 1:
            # from scipy.stats import gini
            from pygini import gini
            gini_coef = gini(np.array(numeric_weights))
            enhanced_indicators['基尼系数'] = f"{gini_coef:.2f}"
        
        # 最大贡献股票
        if symbol_values:
            max_contrib_symbol = max(symbol_values.items(), key=lambda x: x[1])[0]
            max_contrib_weight = symbol_values[max_contrib_symbol] / total_portfolio_value * 100
            enhanced_indicators['最大贡献'] = f"{max_contrib_symbol} ({max_contrib_weight:.2f}%)"
    
    ### 4. 运营效率指标 ###
    
    # 换手率 - 需要交易历史，简化处理
    # 如果只有初始买入，换手率为0
    enhanced_indicators['换手率'] = "0%"
    
    # 费用率 - 需要费用数据，简化处理
    enhanced_indicators['费用率'] = "N/A (需要费用数据)"
    
    # 现金拖累 - 需要现金比例数据，简化处理
    enhanced_indicators['现金拖累'] = "N/A (需要现金数据)"
    
    return enhanced_indicators

def calculate_win_loss_detailed_metrics(daily_returns):
    """
    计算详细的胜率和赔率相关指标
    
    Parameters:
    daily_returns (array): 日收益率数组
    
    Returns:
    dict: 胜率和赔率相关指标
    """
    result = {}
    
    if len(daily_returns) < 10:
        return {'胜率/败率分析': "数据点不足"}
    
    # 区分正收益和负收益
    positive_returns = daily_returns[daily_returns > 0]
    negative_returns = daily_returns[daily_returns < 0]
    
    # 基础胜率
    win_rate = len(positive_returns) / len(daily_returns) * 100
    result['胜率'] = f"{win_rate:.2f}%"
    result['败率'] = f"{100 - win_rate:.2f}%"
    
    # 平均收益和损失
    if len(positive_returns) > 0:
        avg_gain = np.mean(positive_returns) * 100
        result['平均收益(盈利日)'] = f"{avg_gain:.4f}%"
        result['最大单日收益'] = f"{np.max(positive_returns) * 100:.4f}%"
    
    if len(negative_returns) > 0:
        avg_loss = np.mean(negative_returns) * 100
        result['平均损失(亏损日)'] = f"{avg_loss:.4f}%"
        result['最大单日损失'] = f"{np.min(negative_returns) * 100:.4f}%"
    
    # 收益/损失比率 (赔率)
    if len(negative_returns) > 0 and np.mean(negative_returns) != 0:
        gain_loss_ratio = abs(np.mean(positive_returns) / np.mean(negative_returns))
        result['收益/损失比'] = f"{gain_loss_ratio:.2f}"
    
    # 期望值
    expectancy = (win_rate/100 * avg_gain/100) + ((1-win_rate/100) * avg_loss/100) if 'avg_loss' in locals() and 'avg_gain' in locals() else 0
    result['每日期望收益'] = f"{expectancy*100:.4f}%"
    
    # 连续赢/输计数
    win_streak = calculate_streak_metrics(daily_returns > 0)
    loss_streak = calculate_streak_metrics(daily_returns < 0)
    
    result['最大连续盈利天数'] = f"{win_streak['max_streak']}天"
    result['最大连续亏损天数'] = f"{loss_streak['max_streak']}天"
    result['平均连续盈利天数'] = f"{win_streak['avg_streak']:.1f}天"
    result['平均连续亏损天数'] = f"{loss_streak['avg_streak']:.1f}天"
    
    # Z分数 - 衡量收益的稳定性
    if len(daily_returns) > 30:
        z_score = np.mean(daily_returns) / np.std(daily_returns) if np.std(daily_returns) > 0 else 0
        result['收益Z分数'] = f"{z_score:.2f}"
    
    return result

def calculate_streak_metrics(binary_array):
    """
    计算连续事件的统计数据
    
    Parameters:
    binary_array (array): 二进制事件数组
    
    Returns:
    dict: 连续事件统计
    """
    streaks = []
    current_streak = 0
    
    for value in binary_array:
        if value:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
                current_streak = 0
    
    # 处理最后一个连续事件
    if current_streak > 0:
        streaks.append(current_streak)
    
    if not streaks:
        return {'max_streak': 0, 'avg_streak': 0}
    
    return {
        'max_streak': max(streaks),
        'avg_streak': np.mean(streaks)
    }

def calculate_rolling_detailed_metrics(daily_returns, window=20):
    """
    计算详细的滚动指标
    
    Parameters:
    daily_returns (array): 日收益率数组
    window (int): 滚动窗口大小
    
    Returns:
    dict: 滚动指标
    """
    result = {}
    
    if len(daily_returns) < window:
        return {f"{window}日滚动分析": "数据点不足"}
    
    # 使用pandas的rolling函数
    returns_series = pd.Series(daily_returns)
    
    # 各类滚动指标
    rolling_return = returns_series.rolling(window=window).mean() * 252 * 100  # 年化
    rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252) * 100  # 年化
    rolling_sharpe = (returns_series.rolling(window=window).mean() * 252 - 0.02) / (returns_series.rolling(window=window).std() * np.sqrt(252))
    
    # 最新的滚动指标
    result[f"{window}日滚动年化收益"] = f"{rolling_return.iloc[-1]:.2f}%"
    result[f"{window}日滚动年化波动率"] = f"{rolling_vol.iloc[-1]:.2f}%"
    result[f"{window}日滚动夏普比率"] = f"{rolling_sharpe.iloc[-1]:.2f}"
    
    # 最高和最低的滚动指标
    result[f"{window}日最高历史收益"] = f"{rolling_return.max():.2f}%"
    result[f"{window}日最低历史收益"] = f"{rolling_return.min():.2f}%"
    result[f"{window}日最高历史波动率"] = f"{rolling_vol.max():.2f}%"
    result[f"{window}日最低历史波动率"] = f"{rolling_vol[rolling_vol > 0].min() if not rolling_vol[rolling_vol > 0].empty else 0:.2f}%"
    
    # 滚动胜率
    rolling_win_rate = returns_series.rolling(window=window).apply(lambda x: np.sum(x > 0) / len(x) * 100, raw=True)
    result[f"{window}日滚动胜率"] = f"{rolling_win_rate.iloc[-1]:.2f}%"
    
    return result

def calculate_detailed_drawdown_metrics(portfolio_values, dates):
    """
    计算详细的回撤相关指标
    
    Parameters:
    portfolio_values (array): 投资组合价值数组
    dates (list): 对应的日期列表
    
    Returns:
    dict: 回撤相关指标
    """
    result = {}
    
    if len(portfolio_values) < 5:
        return {'回撤分析': "数据点不足"}
    
    # 计算每个时间点的回撤
    drawdowns = []
    peak = portfolio_values[0]
    drawdown_periods = []
    current_drawdown_start = None
    
    for i, value in enumerate(portfolio_values):
        if value > peak:
            peak = value
            if current_drawdown_start is not None:
                current_drawdown_start = None
        else:
            if peak > 0:
                current_drawdown = (peak - value) / peak
                drawdowns.append(current_drawdown)
                
                # 记录新的回撤开始
                if current_drawdown_start is None and current_drawdown > 0.02:  # 只记录超过2%的回撤
                    current_drawdown_start = i
                
                # 记录回撤结束
                if current_drawdown_start is not None and current_drawdown < 0.005:  # 回撤小于0.5%视为结束
                    drawdown_periods.append({
                        'start': current_drawdown_start,
                        'end': i,
                        'depth': max([(peak - portfolio_values[j]) / peak for j in range(current_drawdown_start, i+1)])
                    })
                    current_drawdown_start = None
    
    # 处理可能正在进行的回撤
    if current_drawdown_start is not None:
        drawdown_periods.append({
            'start': current_drawdown_start,
            'end': len(portfolio_values) - 1,
            'depth': max([(peak - portfolio_values[j]) / peak for j in range(current_drawdown_start, len(portfolio_values))])
        })
    
    # 基本回撤统计
    if drawdowns:
        max_drawdown = max(drawdowns) * 100
        avg_drawdown = np.mean(drawdowns) * 100
        result['最大回撤'] = f"{max_drawdown:.2f}%"
        result['平均回撤'] = f"{avg_drawdown:.2f}%"
        
        # 回撤频率
        significant_drawdowns = len([d for d in drawdown_periods if d['depth'] > 0.05])  # 超过5%的显著回撤
        result['显著回撤次数(>5%)'] = str(significant_drawdowns)
        
        # 回撤持续时间统计
        if drawdown_periods and dates:
            durations = []
            for period in drawdown_periods:
                if isinstance(dates[period['start']], (pd.Timestamp, datetime)) and isinstance(dates[period['end']], (pd.Timestamp, datetime)):
                    duration = (dates[period['end']] - dates[period['start']]).days
                    durations.append(duration)
            
            if durations:
                avg_duration = np.mean(durations)
                max_duration = max(durations)
                result['平均回撤持续时间'] = f"{avg_duration:.1f}天"
                result['最长回撤持续时间'] = f"{max_duration}天"
        
        # 历史最大回撤详细信息
        max_dd_period = max(drawdown_periods, key=lambda x: x['depth']) if drawdown_periods else None
        if max_dd_period and dates:
            start_date = dates[max_dd_period['start']]
            end_date = dates[max_dd_period['end']]
            if isinstance(start_date, (pd.Timestamp, datetime)) and isinstance(end_date, (pd.Timestamp, datetime)):
                result['最大回撤开始日期'] = start_date.strftime('%Y-%m-%d')
                result['最大回撤结束日期'] = end_date.strftime('%Y-%m-%d')
                result['最大回撤持续时间'] = f"{(end_date - start_date).days}天"
    
    return result
