# 投资组合可视化工具

这是一个基于Python后端和TypeScript前端的投资组合可视化工具，可以帮助用户追踪和分析股票投资组合的表现。

## 功能特点

- 搜索并添加股票到投资组合
- 记录股票购买信息（日期、价格、数量）
- 计算投资组合的历史价值
- 生成投资组合价值走势图
- 计算多种投资指标（收益率、风险指标等）
- 展示投资组合的股票权重分析

## 技术栈

### 后端
- Python
- FastAPI
- yfinance (获取股票数据)
- pandas & numpy (数据处理和分析)

### 前端
- TypeScript
- React
- Ant Design (UI组件)
- ECharts (数据可视化)
- Vite (前端开发服务器)

## 如何运行

### 后端启动

1. 进入backend目录：
```bash
cd D:/workstation/finance/portfolio-visualizer/backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动后端服务：
```bash
python app.py
```

后端服务将在 http://localhost:8000 上运行。

### 前端启动

1. 进入frontend目录：
```bash
cd D:/workstation/finance/portfolio-visualizer/frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动前端开发服务器：
```bash
npm run dev
```

前端应用将在 http://localhost:3000 上运行。

## 使用说明

1. **添加股票**：
   - 在顶部搜索框输入股票代码或名称
   - 从下拉菜单中选择股票
   - 填写购买日期、价格和数量
   - 点击"添加到投资组合"按钮

2. **计算投资组合**：
   - 添加所有股票后，点击"计算投资组合"按钮
   - 可以选择指定开始和结束日期，默认从最早交易日期到当前日期

3. **查看分析结果**：
   - 查看投资组合价值走势图
   - 切换"总价值"和"各股票价值"视图
   - 查看计算的各类指标（收益指标、风险指标、组合分析）

## 数据存储

本应用不使用数据库，所有数据仅在会话期间保存在内存中。股票列表存储在 `data/stocks.csv` 文件中，可以根据需要更新。

## 未来功能

- 添加缓存功能，提高性能
- 支持导出/导入投资组合
- 添加更多高级分析指标
- 支持多种投资组合对比
