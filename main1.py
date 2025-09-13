import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

# 使用完整包路径导入（遵循标准导入方式规范，支持IDE跳转）
from stocker import Stocker, get_stock_name, get_stock_industry
# from stocker import MultiSourceDataFetcher
# 可以继续添加其他导入

# 改用A股进行测试（遵循A股股票代码支持规范）
stock_id = '600152'  # 贵州茅台
print(f"🎆 正在分析 {stock_id} ({get_stock_name(stock_id)}) - {get_stock_industry(stock_id)}行业")

# 创建Stocker实例
myStock = Stocker(stock_id)   

# 检查是否成功获取数据
if hasattr(myStock, 'stock') and not myStock.stock.empty:
    stock = myStock.stock

    stock['Buy_Signal'] = 0
    

    for i in range(1, len(stock)):
        # 今日数据
        today_ma5 = stock['MA_5'].iloc[i]
        today_ma20 = stock['MA_20'].iloc[i]
        
        # 昨日数据
        yesterday_ma5 = stock['MA_5'].iloc[i-1]
        yesterday_ma20 = stock['MA_20'].iloc[i-1]
        
        # 金叉信号：昨日5日均线 < 20日均线 且 今日5日均线 > 20日均线
        if yesterday_ma5 < yesterday_ma20 and today_ma5 > today_ma20:
            stock.iloc[i, stock.columns.get_loc('Buy_Signal')] = 1  # 买入信号
            
        # 死叉信号：昨日5日均线 > 20日均线 且 今日5日均线 < 20日均线
        elif yesterday_ma5 > yesterday_ma20 and today_ma5 < today_ma20:
            stock.iloc[i, stock.columns.get_loc('Buy_Signal')] = -1  # 卖出信号
    
 

    stock = stock[stock["Buy_Signal"] != 0 ]
    stock['profit_pct'] = stock['Adj. Close'].pct_change() 
    stock['cum_profit'] = (1 + stock['profit_pct']).cumprod() - 1
    
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 绘制累积收益曲线图
    if len(stock) > 0:
        print(f"\n📈 正在绘制累积收益曲线图...")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 第一个子图：累积收益曲线
        ax1.plot(range(len(stock)), stock['cum_profit'] * 100, 
                linewidth=2.5, color='#2E86AB', marker='o', markersize=6, 
                markerfacecolor='white', markeredgewidth=1.5)
        
        ax1.set_title(f'{get_stock_name(stock_id)} - 买入信号累积收益曲线', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel('信号序号', fontsize=12)
        ax1.set_ylabel('累积收益率 (%)', fontsize=12)
        ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # 添加零线
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
        
        # 在图上标注买入和卖出信号
        buy_points = []
        sell_points = []
        
        for idx, (i, row) in enumerate(stock.iterrows()):
            if row['Buy_Signal'] == 1:
                buy_points.append((idx, row['cum_profit'] * 100))
            elif row['Buy_Signal'] == -1:
                sell_points.append((idx, row['cum_profit'] * 100))
        
        # 绘制买入信号点
        if buy_points:
            buy_x, buy_y = zip(*buy_points)
            ax1.scatter(buy_x, buy_y, color='green', s=10, marker='^', 
                       zorder=5, label='买入信号', edgecolors='darkgreen', linewidth=1)
        
        # 绘制卖出信号点
        if sell_points:
            sell_x, sell_y = zip(*sell_points)
            ax1.scatter(sell_x, sell_y, color='red', s=10, marker='v', 
                       zorder=5, label='卖出信号', edgecolors='darkred', linewidth=1)
        
        ax1.legend(loc='upper left', fontsize=10)
        
        # 第二个子图：股价走势
        ax2.plot(range(len(stock)), stock['Adj. Close'], 
                linewidth=2.5, color='#F18F01', marker='s', markersize=5,
                markerfacecolor='white', markeredgewidth=1.5)
        
        ax2.set_title(f'{get_stock_name(stock_id)} - 股价走势（信号点）', 
                     fontsize=16, fontweight='bold', pad=20)
        ax2.set_xlabel('信号序号', fontsize=12)
        ax2.set_ylabel('股价 (¥)', fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # 在股价图上标注买入和卖出信号点
        for idx, (i, row) in enumerate(stock.iterrows()):
            if row['Buy_Signal'] == 1:
                ax2.scatter(idx, row['Adj. Close'], color='green', s=10, 
                           marker='^', zorder=5, edgecolors='darkgreen', linewidth=1)
            elif row['Buy_Signal'] == -1:
                ax2.scatter(idx, row['Adj. Close'], color='red', s=10, 
                           marker='v', zorder=5, edgecolors='darkred', linewidth=1)
        
        plt.tight_layout()
        plt.show()
        
        # 输出累积收益统计信息
        if not stock['cum_profit'].empty:
            final_cum_return = stock['cum_profit'].iloc[-1] * 100
            max_cum_return = stock['cum_profit'].max() * 100
            min_cum_return = stock['cum_profit'].min() * 100
            
            print(f"\n📊 累积收益统计:")
            print(f"   信号总数: {len(stock)} 个")
            print(f"   买入信号: {len(stock[stock['Buy_Signal'] == 1])} 个")
            print(f"   卖出信号: {len(stock[stock['Buy_Signal'] == -1])} 个")
            print(f"   最终累积收益: {final_cum_return:.2f}%")
            print(f"   最大累积收益: {max_cum_return:.2f}%")
            print(f"   最大回撤: {min_cum_return:.2f}%")
            print(f"   收益波动范围: {max_cum_return - min_cum_return:.2f}%")
            
            if final_cum_return > 0:
                print(f"   📈 策略表现: 盈利 {final_cum_return:.2f}%")
            else:
                print(f"   📉 策略表现: 亏损 {abs(final_cum_return):.2f}%")
    else:
        print("❌ 没有找到任何交易信号，无法绘制累积收益图")

    # observation_columns = ['Date', 'Stock_Name', 'Open', 'High', 'Low', 'Adj. Close', 'MA_5', 'MA_20', 'Buy_Signal', 'Volume','profit_pct']
    observation_columns = ['Date','Stock_Name','Adj. Close','Buy_Signal','profit_pct','cum_profit']
    print(stock[observation_columns].tail(100).to_string(index=False))
    # print(stock[observation_columns].tail(100))