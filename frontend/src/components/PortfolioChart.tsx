import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Radio, Card } from 'antd';
import { PortfolioValuePoint } from '../types';

interface PortfolioChartProps {
  data: PortfolioValuePoint[];
}

const PortfolioChart: React.FC<PortfolioChartProps> = ({ data }) => {
  const [chartOption, setChartOption] = useState<any>({});
  const [chartType, setChartType] = useState<string>('total');

  useEffect(() => {
    if (!data || data.length === 0) return;

    // 提取日期和总价值
    const dates = data.map(item => item.Date);
    
    if (chartType === 'total') {
      // 显示总价值图表
      const totalValues = data.map(item => item.TotalValue);
      
      setChartOption({
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const date = params[0].axisValue;
            const value = params[0].data;
            return `日期: ${date}<br/>总价值: ¥${value.toFixed(2)}`;
          }
        },
        xAxis: {
          type: 'category',
          data: dates,
          name: '日期',
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '价值 (¥)',
          axisLabel: {
            formatter: (value: number) => `¥${value.toFixed(0)}`
          }
        },
        series: [{
          name: '投资组合总价值',
          data: totalValues,
          type: 'line',
          smooth: true,
          lineStyle: {
            width: 3,
            color: '#1890ff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(24,144,255,0.3)'
              }, {
                offset: 1, color: 'rgba(24,144,255,0)'
              }]
            }
          }
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        }
      });
    } else {
      // 显示各股票价值图表
      const stockKeys = Object.keys(data[0]).filter(key => 
        key !== 'Date' && key !== 'TotalValue'
      );
      
      const series = stockKeys.map(stock => ({
        name: stock,
        type: 'line',
        stack: '总价值',
        data: data.map(item => item[stock] as number),
        areaStyle: {}
      }));
      
      setChartOption({
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const date = params[0].axisValue;
            let result = `日期: ${date}<br/>`;
            
            params.forEach((param: any) => {
              result += `${param.seriesName}: ¥${param.data.toFixed(2)}<br/>`;
            });
            
            return result;
          }
        },
        legend: {
          data: stockKeys
        },
        xAxis: {
          type: 'category',
          data: dates,
          name: '日期',
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '价值 (¥)',
          axisLabel: {
            formatter: (value: number) => `¥${value.toFixed(0)}`
          }
        },
        series,
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        }
      });
    }
  }, [data, chartType]);

  const handleChartTypeChange = (e: any) => {
    setChartType(e.target.value);
  };

  if (!data || data.length === 0) {
    return <div>没有数据可显示</div>;
  }

  return (
    <div className="chart-container">
      <Radio.Group 
        value={chartType} 
        onChange={handleChartTypeChange}
        style={{ marginBottom: 16 }}
      >
        <Radio.Button value="total">总价值</Radio.Button>
        <Radio.Button value="stocks">各股票价值</Radio.Button>
      </Radio.Group>
      <ReactECharts 
        option={chartOption} 
        style={{ height: '100%', width: '100%' }}
        notMerge={true}
      />
    </div>
  );
};

export default PortfolioChart;
