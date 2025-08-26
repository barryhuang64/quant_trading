#!/usr/bin/env python3
"""
简化的A股股票数据测试
验证 akshare 数据源是否正常工作
"""

import sys
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

from stocker import Stocker

def test_real_a_stock():
    """测试真实A股数据"""
    print("🇨🇳 A股真实数据测试")
    print("=" * 40)
    
    # 测试贵州茅台
    symbol = '600519'
    print(f"📊 测试股票: {symbol} (贵州茅台)")
    
    try:
        # 创建分析器，获取1年数据
        print("🔍 获取贵州茅台近1年数据...")
        moutai = Stocker(symbol)
        
        if hasattr(moutai, 'stock') and not moutai.stock.empty:
            print(f"✅ 数据获取成功!")
            print(f"   数据范围: {moutai.min_date} 到 {moutai.max_date}")
            print(f"   数据量: {len(moutai.stock)} 条")
            print(f"   最新价格: ¥{moutai.most_recent_price:.2f}")
            print(f"   最高价格: ¥{moutai.max_price:.2f}")
            print(f"   最低价格: ¥{moutai.min_price:.2f}")
            
            # 显示最近5天数据
            print(f"\n📋 最近5天数据:")
            recent_data = moutai.stock[['Date', 'Open', 'High', 'Low', 'Adj. Close', 'Volume']].tail(5)
            for _, row in recent_data.iterrows():
                print(f"   {row['Date'].strftime('%Y-%m-%d')}: 开盘¥{row['Open']:.2f} "
                      f"最高¥{row['High']:.2f} 最低¥{row['Low']:.2f} 收盘¥{row['Adj. Close']:.2f}")
            
            # 绘制股价图表
            print(f"\n📈 绘制股价走势图...")
            try:
                moutai.plot_stock(stats=['Adj. Close'])
                plt.title('贵州茅台 (600519) 股价走势')
                plt.ylabel('价格 (¥)')
                plt.show()
                print("✅ 图表显示成功")
            except Exception as plot_error:
                print(f"⚠️ 图表绘制问题: {plot_error}")
            
            return True
            
        else:
            print("❌ 数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_prophet_forecast():
    """测试Prophet预测"""
    print(f"\n🔮 Prophet预测测试")
    print("=" * 40)
    
    try:
        # 使用平安银行进行预测测试（数据比较稳定）
        symbol = '000001'
        print(f"📊 使用股票: {symbol} (平安银行)")
        
        analyzer = Stocker(symbol)
        
        if hasattr(analyzer, 'stock') and not analyzer.stock.empty:
            print("🔄 创建15天预测模型...")
            
            model, forecast_data = analyzer.create_prophet_model(days=15)
            
            # 获取最后的预测价格
            last_prediction = forecast_data.tail(1).iloc[0]
            print(f"✅ 预测成功!")
            print(f"   预测日期: {last_prediction['ds'].strftime('%Y-%m-%d')}")
            print(f"   预测价格: ¥{last_prediction['yhat']:.2f}")
            print(f"   置信区间: ¥{last_prediction['yhat_lower']:.2f} - ¥{last_prediction['yhat_upper']:.2f}")
            
            return True
        else:
            print("❌ 数据获取失败，跳过预测测试")
            return False
            
    except Exception as e:
        print(f"❌ 预测测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🧪 A股股票分析系统验证")
    print("使用 akshare 作为数据源")
    print("=" * 50)
    
    # 测试真实数据获取
    data_success = test_real_a_stock()
    
    # 如果数据获取成功，测试预测功能
    if data_success:
        test_prophet_forecast()
    
    print(f"\n🎉 测试完成!")
    if data_success:
        print("✅ akshare 数据源工作正常")
        print("💡 系统已成功替换 yfinance，使用 akshare 获取A股数据")
    else:
        print("⚠️ akshare 暂时不可用，系统将使用模拟数据")

if __name__ == "__main__":
    main()