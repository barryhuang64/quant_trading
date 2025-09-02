#!/usr/bin/env python3
"""
完整A股股票名称支持演示
展示系统现在可以支持所有A股股票名称查询
"""

import time
from Data_Analysis.stocker import (
    get_stock_name, 
    get_stock_industry,
    search_stocks_by_name,
    get_all_stocks_count,
    show_stock_coverage,
    get_stock_info,
    Stocker
)

def demo_complete_stock_support():
    """演示完整的A股股票支持"""
    print("🎉 完整A股股票名称支持演示")
    print("=" * 60)
    
    # 1. 显示覆盖情况
    print("📊 1. 股票名称覆盖情况")
    print("-" * 40)
    show_stock_coverage()
    
    # 2. 测试各种类型的股票
    print(f"\n📋 2. 测试不同板块股票名称")
    print("-" * 40)
    
    test_stocks = [
        '600519',  # 沪市主板 - 贵州茅台
        '000001',  # 深市主板 - 平安银行
        '300750',  # 创业板 - 宁德时代
        '688981',  # 科创板 - 中芯国际（如果存在）
        '002594',  # 深市中小板 - 比亚迪
        '000858',  # 深市主板 - 五粮液
        '601318',  # 沪市主板 - 中国平安
        '002415',  # 深市中小板 - 海康威视
    ]
    
    print("股票代码  |  股票名称     |  所属行业    |  板块类型")
    print("-" * 60)
    
    for code in test_stocks:
        name = get_stock_name(code)
        industry = get_stock_industry(code)
        
        # 判断板块
        if code.startswith('60'):
            board = '沪市主板'
        elif code.startswith('00'):
            board = '深市主板'
        elif code.startswith('30'):
            board = '创业板'
        elif code.startswith('68'):
            board = '科创板'
        else:
            board = '其他'
            
        print(f"{code:<10} | {name:<12} | {industry:<10} | {board}")
    
    # 3. 搜索功能演示
    print(f"\n🔍 3. 股票名称搜索功能")
    print("-" * 40)
    
    search_keywords = ['银行', '茅台', '比亚迪', '平安']
    
    for keyword in search_keywords:
        print(f"\n搜索关键词: '{keyword}'")
        results = search_stocks_by_name(keyword)
        
        if results:
            print(f"找到 {len(results)} 只相关股票:")
            for i, stock in enumerate(results[:3]):  # 只显示前3个结果
                print(f"   {i+1}. {stock['code']} - {stock['name']} ({stock['industry']})")
            if len(results) > 3:
                print(f"   ... 还有 {len(results)-3} 只股票")
        else:
            print("   未找到相关股票")
    
    # 4. 实际股票数据获取演示
    print(f"\n📈 4. 实际股票数据获取演示")
    print("-" * 40)
    
    demo_code = '000001'  # 平安银行
    print(f"正在获取 {demo_code} 的详细数据...")
    
    try:
        analyzer = Stocker(demo_code)
        
        if hasattr(analyzer, 'stock') and not analyzer.stock.empty:
            stock_data = analyzer.stock
            
            print(f"✅ 数据获取成功!")
            print(f"   股票代码: {stock_data['Stock_Code'].iloc[0]}")
            print(f"   股票名称: {stock_data['Stock_Name'].iloc[0]}")
            print(f"   所属行业: {stock_data['Industry'].iloc[0]}")
            print(f"   数据量: {len(stock_data)} 条")
            print(f"   最新价格: ¥{analyzer.most_recent_price:.2f}")
            
            # 显示最近几天数据
            print(f"\n最近3天数据:")
            recent_data = stock_data[['Date', 'Stock_Name', 'Open', 'High', 'Low', 'Adj. Close']].tail(3)
            print(recent_data.to_string(index=False, float_format='%.2f'))
            
        else:
            print("❌ 数据获取失败")
            
    except Exception as e:
        print(f"❌ 获取数据时出错: {e}")

def demo_random_stocks():
    """随机测试一些股票名称"""
    print(f"\n🎲 5. 随机股票测试")
    print("-" * 40)
    
    # 一些随机的股票代码
    random_codes = [
        '600036',  # 招商银行
        '000002',  # 万科A
        '002236',  # 大华股份
        '600887',  # 伊利股份
        '000895',  # 双汇发展
        '002007',  # 华兰生物
        '300015',  # 爱尔眼科
        '600779',  # 水井坊
    ]
    
    print("随机股票名称测试:")
    print("代码      名称         行业")
    print("-" * 35)
    
    for code in random_codes:
        stock_info = get_stock_info(code)
        print(f"{stock_info['code']}   {stock_info['name']:<10} {stock_info['industry']}")

def main():
    """主函数"""
    print("🚀 A股股票名称完整支持系统")
    print("=" * 60)
    print("✨ 新特性:")
    print("   - 支持所有A股股票名称查询（约5000+只股票）")
    print("   - 自动从 akshare 获取最新股票数据")
    print("   - 本地缓存机制，提高查询效率")
    print("   - 支持按名称搜索股票")
    print("   - 支持沪深主板、创业板、科创板等所有板块")
    print()
    
    try:
        # 运行演示
        demo_complete_stock_support()
        demo_random_stocks()
        
        print(f"\n🎊 演示完成!")
        print(f"💡 总结:")
        print(f"   ✅ 系统现在支持查询所有A股股票名称")
        print(f"   📊 总股票数: {get_all_stocks_count()} 只")
        print(f"   🔄 自动更新：缓存每7天自动刷新一次")
        print(f"   🔍 搜索功能：支持按名称关键词搜索")
        print(f"   📈 完整集成：股票分析中自动显示中文名称")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        print("💡 这可能是因为:")
        print("   1. 网络连接问题")
        print("   2. akshare 版本兼容性问题")
        print("   3. 首次运行需要下载股票数据")

if __name__ == "__main__":
    main()