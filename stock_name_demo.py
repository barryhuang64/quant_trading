#!/usr/bin/env python3
"""
股票名称显示功能演示
展示新增的股票名称列功能
"""

from Data_Analysis.stocker import Stocker, get_stock_name, get_stock_industry

def demo_stock_with_names():
    """演示带股票名称的股票分析"""
    print("🧪 股票名称显示功能演示")
    print("=" * 40)
    
    # 测试几个知名A股
    symbols = ['600519', '000858', '000001']
    
    print("📊 股票基本信息:")
    print("-" * 40)
    
    for symbol in symbols:
        # 直接查询股票名称和行业
        name = get_stock_name(symbol)
        industry = get_stock_industry(symbol)
        print(f"{symbol} | {name} | {industry}")
    
    print(f"\n📈 详细分析 - 贵州茅台 (600519)")
    print("-" * 40)
    
    # 创建分析器
    moutai = Stocker('600519')
    
    if hasattr(moutai, 'stock') and not moutai.stock.empty:
        # 显示带名称的数据
        stock_data = moutai.stock
        
        print(f"✅ 成功获取数据")
        print(f"   股票代码: {stock_data['Stock_Code'].iloc[0]}")
        print(f"   股票名称: {stock_data['Stock_Name'].iloc[0]}")
        print(f"   所属行业: {stock_data['Industry'].iloc[0]}")
        print(f"   数据期间: {moutai.min_date.strftime('%Y-%m-%d')} 到 {moutai.max_date.strftime('%Y-%m-%d')}")
        print(f"   最新价格: ¥{moutai.most_recent_price:.2f}")
        
        # 显示最近几天的数据（包含名称列）
        print(f"\n📋 最近3天数据:")
        recent_columns = ['Date', 'Stock_Name', 'Open', 'High', 'Low', 'Adj. Close', 'Volume']
        recent_data = stock_data[recent_columns].tail(3)
        
        print(recent_data.to_string(index=False, float_format='%.2f'))
        
        print(f"\n💡 现在数据包含以下新列:")
        print(f"   - Stock_Code: 股票代码")
        print(f"   - Stock_Name: 股票中文名称") 
        print(f"   - Industry: 所属行业")
        
    else:
        print("❌ 数据获取失败")

if __name__ == "__main__":
    demo_stock_with_names()