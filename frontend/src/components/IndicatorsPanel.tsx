import React from 'react';
import { Row, Col, Card, Statistic, Divider, List, Typography, Collapse } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Indicators } from '../types';

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface IndicatorsPanelProps {
  indicators: Indicators;
}

// 帮助函数：将任意类型的值转换为字符串，确保安全显示
const safeToString = (value: any): string => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return value.toString();
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

const IndicatorsPanel: React.FC<IndicatorsPanelProps> = ({ indicators }) => {
  // 检查是否有计算错误
  if (indicators.hasOwnProperty('计算错误')) {
    return (
      <Card className="indicator-card">
        <Title level={4} style={{ color: 'red' }}>计算过程中出现错误</Title>
        <Text type="danger">{safeToString(indicators['计算错误'])}</Text>
      </Card>
    );
  }

  // 组织指标为几个主要类别
  const returnIndicators = [
    { key: '总收益率', title: '总收益率', value: indicators['总收益率'] },
    { key: '年化收益率', title: '年化收益率', value: indicators['年化收益率'] },
    { key: '复合年增长率(CAGR)', title: '复合年增长率', value: indicators['复合年增长率(CAGR)'] },
    { key: 'ROI', title: 'ROI', value: indicators['ROI'] },
    { key: '绝对收益', title: '绝对收益', value: indicators['绝对收益'] },
    { key: '时间加权收益率', title: '时间加权收益率', value: indicators['时间加权收益率'] },
    { key: '资金加权收益率', title: '资金加权收益率', value: indicators['资金加权收益率'] }
  ].filter(item => indicators.hasOwnProperty(item.key));

  const riskIndicators = [
    { key: '波动率(年化)', title: '波动率', value: indicators['波动率(年化)'] },
    { key: '日波动率', title: '日波动率', value: indicators['日波动率'] },
    { key: '最大回撤', title: '最大回撤', value: indicators['最大回撤'] },
    { key: '夏普比率', title: '夏普比率', value: indicators['夏普比率'] },
    { key: '卡尔玛比率', title: '卡尔玛比率', value: indicators['卡尔玛比率'] },
    { key: '索提诺比率', title: '索提诺比率', value: indicators['索提诺比率'] },
    { key: '特雷诺比率', title: '特雷诺比率', value: indicators['特雷诺比率'] },
    { key: '风险值(VaR 95%)', title: 'VaR 95%', value: indicators['风险值(VaR 95%)'] },
    { key: '条件风险值(CVaR 95%)', title: 'CVaR 95%', value: indicators['条件风险值(CVaR 95%)'] },
    { key: '下行偏差', title: '下行偏差', value: indicators['下行偏差'] }
  ].filter(item => indicators.hasOwnProperty(item.key));
  
  // 阿尔法/贝塔分析
  const alphaBetaIndicators = [
    { key: '阿尔法', title: '阿尔法', value: indicators['阿尔法'] },
    { key: '贝塔', title: '贝塔', value: indicators['贝塔'] },
    { key: '信息比率', title: '信息比率', value: indicators['信息比率'] }
  ].filter(item => indicators.hasOwnProperty(item.key));

  // 获取胜率/败率分析的详细指标
  const detailedWinLossIndicators = indicators['胜负详细分析'] as Record<string, string> || {};
  const winLossIndicators = [
    { key: '胜率', title: '胜率', value: detailedWinLossIndicators['胜率'] || indicators['胜率'] },
    { key: '败率', title: '败率', value: detailedWinLossIndicators['败率'] || indicators['败率'] },
    { key: '平均收益(盈利日)', title: '平均盈利', value: detailedWinLossIndicators['平均收益(盈利日)'] || indicators['平均收益'] },
    { key: '平均损失(亏损日)', title: '平均亏损', value: detailedWinLossIndicators['平均损失(亏损日)'] || indicators['平均损失'] },
    { key: '收益/损失比', title: '收益/损失比', value: detailedWinLossIndicators['收益/损失比'] || indicators['收益损失比'] },
    { key: '最大单日收益', title: '最大单日收益', value: detailedWinLossIndicators['最大单日收益'] },
    { key: '最大单日损失', title: '最大单日损失', value: detailedWinLossIndicators['最大单日损失'] },
    { key: '最大连续盈利天数', title: '最大连续盈利', value: detailedWinLossIndicators['最大连续盈利天数'] || indicators['最长连续上涨天数'] },
    { key: '最大连续亏损天数', title: '最大连续亏损', value: detailedWinLossIndicators['最大连续亏损天数'] || indicators['最长连续下跌天数'] },
    { key: '每日期望收益', title: '每日期望收益', value: detailedWinLossIndicators['每日期望收益'] }
  ].filter(item => item.value);
  
  // 获取滚动分析指标
  const rolling20Data = indicators['20日滚动分析'] as Record<string, string> || {};
  const rolling60Data = indicators['60日滚动分析'] as Record<string, string> || {};
  const rollingIndicators = [
    { key: '20日滚动年化收益', title: '20日滚动收益', value: rolling20Data['20日滚动年化收益'] || indicators['20日滚动年化收益率(中位数)'] },
    { key: '20日滚动年化波动率', title: '20日滚动波动率', value: rolling20Data['20日滚动年化波动率'] || indicators['20日滚动年化波动率(中位数)'] },
    { key: '20日滚动夏普比率', title: '20日滚动夏普比率', value: rolling20Data['20日滚动夏普比率'] },
    { key: '20日滚动胜率', title: '20日滚动胜率', value: rolling20Data['20日滚动胜率'] },
    { key: '60日滚动年化收益', title: '60日滚动收益', value: rolling60Data['60日滚动年化收益'] || indicators['60日滚动年化收益率(中位数)'] },
    { key: '60日滚动年化波动率', title: '60日滚动波动率', value: rolling60Data['60日滚动年化波动率'] || indicators['60日滚动年化波动率(中位数)'] },
    { key: '60日滚动夏普比率', title: '60日滚动夏普比率', value: rolling60Data['60日滚动夏普比率'] }
  ].filter(item => item.value);
  
  // 回撤分析指标
  const drawdownInfo: Record<string, string> = {};
  const detailedDrawdown = indicators['回撤详细分析'] as Record<string, string | number> || {};
  
  // 添加新的回撤分析指标
  if (Object.keys(detailedDrawdown).length > 0) {
    for (const [key, value] of Object.entries(detailedDrawdown)) {
      drawdownInfo[key] = safeToString(value);
    }
  } else {
    // 兼容旧版指标
    for (const [key, value] of Object.entries(indicators)) {
      if (
        key.includes('最大回撤') || 
        key.includes('回撤') || 
        key.includes('显著回撤') || 
        key.includes('平均回撤')
      ) {
        drawdownInfo[key] = safeToString(value);
      }
    }
  }
  
  // 获取多元化分析指标
  const diversificationIndicators = [
    { key: '权重集中度(HHI)', title: '权重集中度', value: indicators['权重集中度(HHI)'] },
    { key: '基尼系数', title: '基尼系数', value: indicators['基尼系数'] },
    { key: '投资集中度(基尼系数)', title: '投资集中度', value: indicators['投资集中度(基尼系数)'] },
    { key: '投资多样性(熵值)', title: '投资多样性', value: indicators['投资多样性(熵值)'] }
  ].filter(item => indicators.hasOwnProperty(item.key));

  // 处理股票权重，如果有的话
  let weightItems: {title: string, value: string}[] = [];
  if (indicators['股票权重']) {
    const weights = indicators['股票权重'] as Record<string, string>;
    weightItems = Object.entries(weights).map(([symbol, weight]) => ({
      title: symbol,
      value: weight
    }));
  }

  // 判断是收益还是亏损，用于颜色显示
  const isProfit = returnIndicators.length > 0 ? 
    parseFloat(String(returnIndicators[0].value).replace('%', '')) > 0 : false;

  return (
    <div>
      <Title level={4}>投资组合分析指标</Title>
      
      <Row gutter={[16, 16]}>
        {/* 收益指标 */}
        <Col xs={24} sm={24} md={8}>
          <Card title="收益指标" className="indicator-card">
            {returnIndicators.map((indicator, index) => (
              <Statistic
                key={indicator.key}
                title={indicator.title}
                value={safeToString(indicator.value)}
                valueStyle={{ color: isProfit ? '#3f8600' : '#cf1322' }}
                prefix={isProfit ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                style={{ marginBottom: index !== returnIndicators.length - 1 ? 16 : 0 }}
              />
            ))}
            {returnIndicators.length === 0 && <Text type="secondary">没有可用的收益指标</Text>}
          </Card>
        </Col>

        {/* 风险指标 */}
        <Col xs={24} sm={24} md={8}>
          <Card title="风险指标" className="indicator-card">
            {riskIndicators.map((indicator, index) => (
              <Statistic
                key={indicator.key}
                title={indicator.title}
                value={safeToString(indicator.value)}
                style={{ marginBottom: index !== riskIndicators.length - 1 ? 16 : 0 }}
              />
            ))}
            {riskIndicators.length === 0 && <Text type="secondary">没有可用的风险指标</Text>}
          </Card>
        </Col>

        {/* 其他指标和组合分析 */}
        <Col xs={24} sm={24} md={8}>
          <Card title="组合分析" className="indicator-card">
            {indicators['最大贡献'] && (
              <Statistic
                title="最大贡献股票"
                value={safeToString(indicators['最大贡献'])}
                style={{ marginBottom: 16 }}
              />
            )}
            
            {weightItems.length > 0 && (
              <>
                <Divider style={{ margin: '12px 0' }} />
                <Title level={5}>股票权重</Title>
                <List
                  size="small"
                  dataSource={weightItems}
                  renderItem={item => (
                    <List.Item>
                      <Text>{item.title}:</Text>
                      <Text strong>{item.value}</Text>
                    </List.Item>
                  )}
                />
              </>
            )}
            
            {weightItems.length === 0 && !indicators['最大贡献'] && 
              <Text type="secondary">没有可用的组合分析</Text>}
          </Card>
        </Col>
      </Row>
      
      {/* 新增区域：胜率/败率分析 */}
      {winLossIndicators.length > 0 && (
        <>
          <Divider />
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title="胜率/败率分析" className="indicator-card">
                <Row gutter={[16, 16]}>
                  {winLossIndicators.map(indicator => (
                    <Col xs={24} sm={12} md={8} lg={6} key={indicator.key}>
                      <Statistic
                        title={indicator.title}
                        value={safeToString(indicator.value)}
                      />
                    </Col>
                  ))}
                </Row>
              </Card>
            </Col>
          </Row>
        </>
      )}
      
      {/* 新增区域：滚动分析 */}
      {rollingIndicators.length > 0 && (
        <>
          <Divider />
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title="滚动分析" className="indicator-card">
                <Row gutter={[16, 16]}>
                  {rollingIndicators.map(indicator => (
                    <Col xs={24} sm={12} md={8} lg={6} key={indicator.key}>
                      <Statistic
                        title={indicator.title}
                        value={safeToString(indicator.value)}
                      />
                    </Col>
                  ))}
                </Row>
              </Card>
            </Col>
          </Row>
        </>
      )}
      
      {/* 新增区域：详细回撤分析 */}
      {Object.keys(drawdownInfo).length > 0 && (
        <>
          <Divider />
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title="详细回撤分析" className="indicator-card">
                <Collapse ghost>
                  <Panel header="查看详细回撤指标" key="1">
                    <List
                      size="small"
                      dataSource={Object.entries(drawdownInfo)}
                      renderItem={([key, value]) => (
                        <List.Item>
                          <Text>{key}:</Text>
                          <Text strong>{value}</Text>
                        </List.Item>
                      )}
                    />
                  </Panel>
                </Collapse>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
};

export default IndicatorsPanel;
