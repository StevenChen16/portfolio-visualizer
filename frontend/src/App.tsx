import React, { useState } from 'react';
import { Layout, Typography, Row, Col, Card, Divider, Button, Dropdown, Space } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import StockSearch from './components/StockSearch';
import PortfolioTable from './components/PortfolioTable';
import PortfolioChart from './components/PortfolioChart';
import IndicatorsPanel from './components/IndicatorsPanel';
import { StockTransaction } from './types';
import { useTranslation } from 'react-i18next';
// 引入i18n配置
import './i18n/i18n';

// Logo图片可以放在这里导入
// import Logo from './assets/images/logo.png';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const { t, i18n } = useTranslation();
  
  // 存储投资组合交易
  const [transactions, setTransactions] = useState<StockTransaction[]>([]);
  
  // 存储计算的投资组合价值数据
  const [portfolioValue, setPortfolioValue] = useState<any[]>([]);
  
  // 存储计算的指标
  const [indicators, setIndicators] = useState<any>({});
  
  // 切换语言函数
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  // 添加新交易
  const addTransaction = (transaction: StockTransaction) => {
    setTransactions([...transactions, transaction]);
  };

  // 删除交易
  const removeTransaction = (index: number) => {
    const updatedTransactions = [...transactions];
    updatedTransactions.splice(index, 1);
    setTransactions(updatedTransactions);
  };

  // 更新投资组合数据和指标
  const updatePortfolioData = (value: any[], indicators: any) => {
    setPortfolioValue(value);
    setIndicators(indicators);
  };

  return (
    <Layout>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div className="logo" style={{ marginRight: '16px' }}>
            {/* 当有Logo时可以取消下面的注释 */}
            {/* <img src={Logo} alt="Portfolio Visualizer Logo" style={{ height: '32px' }} /> */}
          </div>
          <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
            {t('appTitle')}
          </Title>
        </div>
        <Space>
          <Dropdown menu={{ 
            items: [
              { key: 'en', label: 'English', onClick: () => changeLanguage('en') },
              { key: 'zh', label: '中文', onClick: () => changeLanguage('zh') }
            ] as any
          }} placement="bottomRight">
            <Button icon={<GlobalOutlined />}>
              {i18n.language === 'zh' ? '中文' : 'English'}
            </Button>
          </Dropdown>
        </Space>
      </Header>
      <Content style={{ padding: '0 50px' }}>
        <div className="site-layout-content">
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title={t('addStock')}>
                <StockSearch onSelect={addTransaction} />
              </Card>
            </Col>
          </Row>
          <Divider />
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <PortfolioTable 
                transactions={transactions} 
                onRemove={removeTransaction}
                onCalculate={updatePortfolioData}
              />
            </Col>
          </Row>
          {portfolioValue.length > 0 && (
            <>
              <Divider />
              <Row gutter={[16, 16]}>
                <Col span={24}>
                  <Card title={t('charts.portfolioValue')}>
                    <PortfolioChart data={portfolioValue} />
                  </Card>
                </Col>
              </Row>
            </>
          )}
          {Object.keys(indicators).length > 0 && (
            <>
              <Divider />
              <Row gutter={[16, 16]}>
                <Col span={24}>
                  <IndicatorsPanel indicators={indicators} />
                </Col>
              </Row>
            </>
          )}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        {t('appTitle')} ©{new Date().getFullYear()} {t('footer.createdBy')} <a href="https://amplimit.com" target="_blank" rel="noopener noreferrer">Amplimit</a>
      </Footer>
    </Layout>
  );
};

export default App;
