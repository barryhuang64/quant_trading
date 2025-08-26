#!/usr/bin/env python3
"""
A股股票数据获取测试
使用 akshare 作为主要数据源，替代 yfinance
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

# 使用已安装的包进行导入（遵循标准导入方式规范）
from stocker import Stocker

def test_a_stock_data():
    """测试A股数据获取"""
    print("🚀 开始测试A股数据获取...")
    print("=" * 50)
    
    # 测试A股数据 - 选择一些知名的A股股票
    test_symbols = [
        '600519',  # 贵州茅台
        '000858',  # 五粮液  
        '000001',  # 平安银行
        '000002',  # 万科A
        '600036',  # 招商银行
    ]
    
    # 股票名称映射（用于显示）
    stock_names = {
        '600519': '贵州茅台',
        '000858': '五粮液',
        '000001': '平安银行', 
        '000002': '万科A',
        '600036': '招商银行',
    }
    
    successful_stocks = []
    
    for symbol in test_symbols:
        stock_name = stock_names.get(symbol, symbol)
        print(f"\n📊 测试A股: {symbol} ({stock_name})")
        print("-" * 40)
        
        try:
            # 创建 Stocker 实例
            print(f"🔍 正在获取 {stock_name} 的数据...")
            stock_analyzer = Stocker(symbol)
            
            # 检查数据获取是否成功
            if hasattr(stock_analyzer, 'stock') and not stock_analyzer.stock.empty:
                print(f"✅ {stock_name} 数据获取成功!")
                print(f"   数据范围: {stock_analyzer.min_date} 到 {stock_analyzer.max_date}")
                print(f"   数据条数: {len(stock_analyzer.stock)}")
                print(f"   当前价格: ¥{stock_analyzer.most_recent_price:.2f}")
                
                # 显示前几行数据
                print(f"\n📋 {stock_name} 数据预览:")
                display_data = stock_analyzer.stock[['Date', 'Open', 'High', 'Low', 'Adj. Close', 'Volume']].head(3)
                print(display_data.to_string(index=False))
                
                successful_stocks.append((symbol, stock_name, stock_analyzer))
                
            else:
                print(f"❌ {stock_name} 数据获取失败")
                
        except Exception as e:
            print(f"❌ {stock_name} 处理出错: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"📈 成功获取 {len(successful_stocks)} 只股票的数据")
    
    return successful_stocks

def test_stock_analysis(successful_stocks):
    """测试股票分析功能"""
    if not successful_stocks:
        print("⚠️ 没有成功获取的股票数据，跳过分析测试")
        return
    
    print(f"\n🔍 开始股票分析测试...")
    print("=" * 50)
    
    # 选择第一个成功的股票进行分析
    symbol, stock_name, analyzer = successful_stocks[0]
    
    print(f"📊 使用 {stock_name} ({symbol}) 进行分析测试")
    
    try:
        # 1. 基本价格统计
        print(f"\n💰 {stock_name} 价格统计:")
        print(f"   最高价格: ¥{analyzer.max_price:.2f} (日期: {analyzer.max_price_date.strftime('%Y-%m-%d')})")
        print(f"   最低价格: ¥{analyzer.min_price:.2f} (日期: {analyzer.min_price_date.strftime('%Y-%m-%d')})")
        print(f"   起始价格: ¥{analyzer.starting_price:.2f}")
        print(f"   最新价格: ¥{analyzer.most_recent_price:.2f}")
        
        # 2. 基本股价图表
        print(f"\n📈 绘制 {stock_name} 股价图表...")
        try:
            analyzer.plot_stock(stats=['Adj. Close'])
            plt.title(f'{stock_name} ({symbol}) 股价走势')
            plt.ylabel('价格 (¥)')
            plt.show()
            print(f"✅ {stock_name} 股价图表显示成功")
        except Exception as plot_error:
            print(f"⚠️ 图表绘制问题: {plot_error}")
        
    except Exception as analysis_error:
        print(f"❌ 股票分析失败: {analysis_error}")

def test_prophet_prediction(successful_stocks):
    """测试Prophet预测模型"""
    if not successful_stocks:
        print("⚠️ 没有成功获取的股票数据，跳过预测测试")
        return
    
    print(f"\n🔮 开始Prophet预测测试...")
    print("=" * 50)
    
    # 选择第一个成功的股票进行预测
    symbol, stock_name, analyzer = successful_stocks[0]
    
    print(f"🚀 使用 {stock_name} ({symbol}) 进行预测测试")
    
    try:
        # 创建30天预测模型
        print(f"🔄 创建 {stock_name} 的30天预测模型...")
        model, model_data = analyzer.create_prophet_model(days=30)
        print(f"✅ {stock_name} Prophet模型创建成功")
        
        # 显示预测结果
        future_data = model_data.tail(30)  # 获取未来30天的预测
        latest_prediction = future_data.iloc[-1]
        print(f"📅 预测日期: {latest_prediction['ds'].strftime('%Y-%m-%d')}")
        print(f"💰 预测价格: ¥{latest_prediction['yhat']:.2f}")
        print(f"📊 置信区间: ¥{latest_prediction['yhat_lower']:.2f} - ¥{latest_prediction['yhat_upper']:.2f}")
        
        # 安全的组件图绘制
        try:
            model.plot_components(model_data)
            plt.suptitle(f'{stock_name} ({symbol}) Prophet模型组件分析')
            plt.tight_layout()
            plt.show()
            print(f"📊 {stock_name} 组件分解图显示成功")
        except Exception as plot_error:
            print(f"⚠️ 组件图绘制问题: {plot_error}")
        
        # 变点分析
        try:
            print(f"\n🔍 {stock_name} 变点分析...")
            analyzer.changepoint_date_analysis()
            print(f"✅ {stock_name} 变点分析完成")
        except Exception as analysis_error:
            print(f"⚠️ 变点分析问题: {analysis_error}")
            
    except Exception as model_error:
        print(f"❌ {stock_name} 预测模型失败: {model_error}")

def test_data_sources_directly():
    """直接测试数据源模块"""
    print(f"\n🧪 直接测试数据源模块...")
    print("=" * 50)
    
    from stocker import MultiSourceDataFetcher
    
    try:
        # 创建数据获取器
        fetcher = MultiSourceDataFetcher()
        
        # 测试获取贵州茅台数据
        print("🍺 测试获取贵州茅台 (600519) 数据...")
        stock_data, data_source = fetcher.fetch_stock_data('600519', 'max')
        
        print(f"✅ 数据获取成功!")
        print(f"   数据源: {data_source}")
        print(f"   数据量: {len(stock_data)} 条")
        print(f"   数据范围: {stock_data['Date'].min()} 到 {stock_data['Date'].max()}")
        
        # 显示数据样例
        print("\n📊 数据样例:")
        print(stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].head().to_string(index=False))
        
    except Exception as e:
        print(f"❌ 直接测试数据源失败: {str(e)}")

def main():
    """主测试函数"""
    print("🇨🇳 A股股票分析系统测试")
    print("=" * 60)
    print("📌 使用 akshare 作为主要数据源")
    print("📌 测试对象：A股知名股票")
    
    # 1. 测试A股数据获取
    successful_stocks = test_a_stock_data()
    
    # 2. 测试股票分析功能
    test_stock_analysis(successful_stocks)
    
    # 3. 测试Prophet预测
    test_prophet_prediction(successful_stocks)
    
    # 4. 直接测试数据源模块
    test_data_sources_directly()
    
    print(f"\n🎊 A股测试完成!")
    print("💡 如果看到模拟数据，说明akshare暂时不可用，系统自动降级到模拟数据")
    print("💡 系统优先使用 akshare 获取A股数据，然后尝试 tushare，最后降级到模拟数据")
    print("💡 建议网络良好时运行，akshare需要访问网络获取实时数据")

if __name__ == "__main__":
    main()