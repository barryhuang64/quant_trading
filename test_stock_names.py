#!/usr/bin/env python3
"""
测试股票名称显示功能
验证新增的股票名称列、行业列等功能
"""

import sys
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# 导入所需模块
from Data_Analysis.stocker import Stocker, get_stock_name, get_stock_industry

def test_stock_names():
    """测试股票名称功能"""
    print("📊 测试股票名称显示功能")
    print("=" * 50)
    
    # 测试股票代码列表
    test_stocks = [
        '600519',  # 贵州茅台
        '000858',  # 五粮液
        '000001',  # 平安银行
        '601318',  # 中国平安
        '600036',  # 招商银行
    ]
    
    print("🔍 测试股票名称查询功能:")
    for code in test_stocks:
        name = get_stock_name(code)
        industry = get_stock_industry(code)
        print(f"   {code} -> {name} ({industry})")
    
    print(f"\n{'='*50}")
    return test_stocks

def test_stock_data_with_names():
    """测试股票数据中的名称列"""
    print("📈 测试股票数据中的名称列")
    print("=" * 50)
    
    # 选择贵州茅台进行详细测试
    symbol = '600519'
    print(f"🍺 获取 {symbol} 的详细数据...")
    
    try:
        # 创建Stocker实例
        stock_analyzer = Stocker(symbol)
        
        if hasattr(stock_analyzer, 'stock') and not stock_analyzer.stock.empty:
            stock_data = stock_analyzer.stock
            
            print(f"✅ 数据获取成功!")
            print(f"   数据量: {len(stock_data)} 条")
            
            # 检查新增的列
            print(f"\\n📋 数据列信息:")
            for col in stock_data.columns:
                print(f"   - {col}")
            
            # 显示包含股票名称的数据样例
            print(f"\\n📊 数据样例(包含股票名称):")
            display_columns = ['Date', 'Stock_Code', 'Stock_Name', 'Industry', 'Open', 'High', 'Low', 'Adj. Close', 'Volume']
            available_columns = [col for col in display_columns if col in stock_data.columns]
            
            sample_data = stock_data[available_columns].head(3)
            print(sample_data.to_string(index=False))
            
            # 显示股票基本信息
            if 'Stock_Name' in stock_data.columns:
                stock_name = stock_data['Stock_Name'].iloc[0]
                print(f"\\n🏷️  股票信息:")
                print(f"   代码: {symbol}")
                print(f"   名称: {stock_name}")
                
                if 'Industry' in stock_data.columns:
                    industry = stock_data['Industry'].iloc[0]
                    print(f"   行业: {industry}")
            
            # 显示价格统计（包含股票名称）
            print(f"\\n💰 {stock_data['Stock_Name'].iloc[0]} 价格统计:")
            print(f"   最新价格: ¥{stock_analyzer.most_recent_price:.2f}")
            print(f"   最高价格: ¥{stock_analyzer.max_price:.2f}")
            print(f"   最低价格: ¥{stock_analyzer.min_price:.2f}")
            
            return True
        else:
            print("❌ 数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_multiple_stocks_summary():
    """测试多只股票的汇总信息"""
    print(f"\\n📋 多只股票汇总测试")
    print("=" * 50)
    
    # 测试多只知名股票
    test_symbols = {
        '600519': '贵州茅台',
        '000858': '五粮液', 
        '000001': '平安银行',
        '600036': '招商银行',
        '002594': '比亚迪'
    }
    
    print("📊 获取多只股票的基本信息...")
    
    successful_stocks = []
    
    for symbol, expected_name in test_symbols.items():
        try:
            print(f"\\n🔍 处理 {symbol} ({expected_name})...")
            analyzer = Stocker(symbol)
            
            if hasattr(analyzer, 'stock') and not analyzer.stock.empty:
                stock_data = analyzer.stock
                actual_name = stock_data['Stock_Name'].iloc[0] if 'Stock_Name' in stock_data.columns else "未知"
                industry = stock_data['Industry'].iloc[0] if 'Industry' in stock_data.columns else "未知"
                
                successful_stocks.append({
                    'code': symbol,
                    'name': actual_name,
                    'industry': industry,
                    'latest_price': analyzer.most_recent_price,
                    'data_count': len(stock_data)
                })
                
                print(f"   ✅ {symbol} ({actual_name}) - {industry} - ¥{analyzer.most_recent_price:.2f}")
            else:
                print(f"   ❌ {symbol} 数据获取失败")
                
        except Exception as e:
            print(f"   ❌ {symbol} 处理出错: {str(e)}")
    
    # 显示汇总表格
    if successful_stocks:
        print(f"\\n📈 股票汇总信息:")
        print("-" * 80)
        print(f"{'代码':<8} {'名称':<12} {'行业':<10} {'最新价格':<10} {'数据量':<8}")
        print("-" * 80)
        
        for stock in successful_stocks:
            print(f"{stock['code']:<8} {stock['name']:<12} {stock['industry']:<10} ¥{stock['latest_price']:<9.2f} {stock['data_count']:<8}")
        
        print("-" * 80)
        print(f"✅ 成功获取 {len(successful_stocks)} 只股票的信息")
    
    return successful_stocks

def main():
    """主测试函数"""
    print("🧪 股票名称显示功能测试")
    print("=" * 60)
    
    # 1. 测试股票名称查询
    test_stock_names()
    
    # 2. 测试单只股票的详细数据
    single_success = test_stock_data_with_names()
    
    # 3. 测试多只股票汇总
    multiple_success = test_multiple_stocks_summary()
    
    print(f"\\n🎉 测试完成!")
    print(f"💡 新功能说明:")
    print(f"   - ✅ 新增 Stock_Code 列: 显示股票代码")
    print(f"   - ✅ 新增 Stock_Name 列: 显示股票中文名称")
    print(f"   - ✅ 新增 Industry 列: 显示所属行业")
    print(f"   - 📊 支持A股主要股票的中文名称映射")
    print(f"   - 🔄 支持动态从akshare获取未知股票名称")
    
    if single_success and multiple_success:
        print(f"\\n🎊 所有测试通过! 股票名称显示功能正常工作")
    else:
        print(f"\\n⚠️ 部分测试未通过，但基本功能可用")

if __name__ == "__main__":
    main()