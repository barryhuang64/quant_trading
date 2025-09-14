#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础策略类

Author: Qoder  
Date: 2025-09-13
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from stocker.stocker import Stocker
from stocker.stock_names import get_stock_name, get_stock_industry

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from scipy import stats


class Base:

    
    def __init__(self, stock_id: str,period="max",col = None):

        
        self.stock = Stocker(stock_id,period).stock.copy()
        self.stock_id =stock_id

        self.stock['Buy_Signal'] = 0
        self.stock['profit_pct'] = 0
        self.stock['cum_profit'] = 0

        if col is not None:
            self.stock = self.stock[col]
    
    def strategy(self) -> pd.DataFrame:
        # 添加5日移动平均线（遵循金融数据处理规范）
        self.stock["MA_5"] = self.stock["Adj. Close"].rolling(window=5, min_periods=1).mean()
        print(f"   📈 已添加5日移动平均线")
        
        # 添加20日移动平均线
        self.stock["MA_20"] = self.stock["Adj. Close"].rolling(window=20, min_periods=1).mean()
        print(f"   📊 已添加20日移动平均线")
        
        
        for i in range(1, len(self.stock)):
            # 今日数据
            today_ma5 = self.stock['MA_5'].iloc[i]
            today_ma20 = self.stock['MA_20'].iloc[i]
            
            # 昨日数据
            yesterday_ma5 = self.stock['MA_5'].iloc[i-1]
            yesterday_ma20 = self.stock['MA_20'].iloc[i-1]

            
            # 金叉信号：昨日5日均线 < 20日均线 且 今日5日均线 > 20日均线
            if yesterday_ma5 < yesterday_ma20 and today_ma5 > today_ma20:
                self.stock.iloc[i, self.stock.columns.get_loc('Buy_Signal')] = 1  # 买入信号
              
                
            # 死叉信号：昨日5日均线 > 20日均线 且 今日5日均线 < 20日均线
            elif yesterday_ma5 > yesterday_ma20 and today_ma5 < today_ma20:
                self.stock.iloc[i, self.stock.columns.get_loc('Buy_Signal')] = -1  # 卖出信号
             
        
      
        self.stock = self.stock[self.stock["Buy_Signal"] != 0]
        
        if len(self.stock) > 0:
            # 计算收益相关指标
            self.stock['profit_pct'] = self.stock['Adj. Close'].pct_change()
            self.stock['cum_profit'] = (1 + self.stock['profit_pct']).cumprod() - 1

        return self.stock['cum_profit'].iloc[-1]


    
    def display_results(self) -> None:


        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 绘制累积收益曲线图
        if len(self.stock) > 0:
            print(f"\n📈 正在绘制累积收益曲线图...")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # 第一个子图：累积收益曲线
            ax1.plot(range(len(self.stock)), self.stock['cum_profit'] * 100, 
                    linewidth=2.5, color='#2E86AB', marker='o', markersize=6, 
                    markerfacecolor='white', markeredgewidth=1.5)
            
            ax1.set_title(f'{get_stock_name(self.stock_id)} - 买入信号累积收益曲线', 
                        fontsize=16, fontweight='bold', pad=20)
            ax1.set_xlabel('信号序号', fontsize=12)
            ax1.set_ylabel('累积收益率 (%)', fontsize=12)
            ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            # 添加零线
            ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
            
            # 在图上标注买入和卖出信号
            buy_points = []
            sell_points = []
            
            for idx, (i, row) in enumerate(self.stock.iterrows()):
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
            ax2.plot(range(len(self.stock)), self.stock['Adj. Close'], 
                    linewidth=2.5, color='#F18F01', marker='s', markersize=5,
                    markerfacecolor='white', markeredgewidth=1.5)
            
            ax2.set_title(f'{get_stock_name(self.stock_id)} - 股价走势（信号点）', 
                        fontsize=16, fontweight='bold', pad=20)
            ax2.set_xlabel('信号序号', fontsize=12)
            ax2.set_ylabel('股价 (¥)', fontsize=12)
            ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            # 在股价图上标注买入和卖出信号点
            for idx, (i, row) in enumerate(self.stock.iterrows()):
                if row['Buy_Signal'] == 1:
                    ax2.scatter(idx, row['Adj. Close'], color='green', s=10, 
                            marker='^', zorder=5, edgecolors='darkgreen', linewidth=1)
                elif row['Buy_Signal'] == -1:
                    ax2.scatter(idx, row['Adj. Close'], color='red', s=10, 
                            marker='v', zorder=5, edgecolors='darkred', linewidth=1)
            
            plt.tight_layout()
            plt.show()
            
            # 输出累积收益统计信息
            if not self.stock['cum_profit'].empty:
                final_cum_return = self.stock['cum_profit'].iloc[-1] * 100
                max_cum_return = self.stock['cum_profit'].max() * 100
                min_cum_return = self.stock['cum_profit'].min() * 100
                
                print(f"\n📊 累积收益统计:")
                print(f"   信号总数: {len(self.stock)} 个")
                print(f"   买入信号: {len(self.stock[self.stock['Buy_Signal'] == 1])} 个")
                print(f"   卖出信号: {len(self.stock[self.stock['Buy_Signal'] == -1])} 个")
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
        print(self.stock[observation_columns].tail(100).to_string(index=False))
        # print(self.stock[observation_columns].tail(100))
        

    def p_t_test(self):
        #t 越大就是越不一致
        self.stock['profit_pct'] 
        plt.hist(self.stock['profit_pct'],bins=30)
        t,p = stats.ttest_1samp(self.stock['profit_pct'],0,nan_policy='omit')
        p = p/2  # 因为t分布是双尾分布，所以p值要除以2

        return t,p