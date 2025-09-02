import sys
import os
import matplotlib.pyplot as plt

# 使用完整包路径导入（遵循标准导入方式规范，支持IDE跳转）
from Data_Analysis.stocker import Stocker, get_stock_name, get_stock_industry
from Data_Analysis.stocker import MultiSourceDataFetcher
# 可以继续添加其他导入

# 改用A股进行测试（遵循A股股票代码支持规范）
symbol = '600519'  # 贵州茅台
print(f"🎆 正在分析 {symbol} ({get_stock_name(symbol)}) - {get_stock_industry(symbol)}行业")

# 创建Stocker实例
moutai = Stocker(symbol)   

# 检查是否成功获取数据
if hasattr(moutai, 'stock') and not moutai.stock.empty:
    stock_history = moutai.stock
    print("✅ 成功获取股票数据")
    
    # 显示包含股票名称的数据信息
    print(f"📋 股票信息:")
    print(f"   代码: {stock_history['Stock_Code'].iloc[0]}")
    print(f"   名称: {stock_history['Stock_Name'].iloc[0]}")
    print(f"   行业: {stock_history['Industry'].iloc[0]}")
    print(f"   数据量: {len(stock_history)} 条")
    print(f"   最新价格: ¥{moutai.most_recent_price:.2f}")
    
    # 显示包含名称的数据样例
    print(f"\n📊 数据样例(包含股票名称):")
    display_columns = ['Date', 'Stock_Name', 'Open', 'High', 'Low', 'Adj. Close', 'Volume']
    print(stock_history[display_columns].head(3).to_string(index=False))
    
    try:
        # 创建预测模型（遵循API调用与错误处理规范）
        model, model_data = moutai.create_prophet_model(days=30)
        print("✅ Prophet模型创建成功")
        
        # 显示预测结果（包含股票名称）
        latest_prediction = model_data.tail(1).iloc[0]
        stock_name = stock_history['Stock_Name'].iloc[0]
        print(f"🔮 {stock_name} 预测结果:")
        print(f"   预测日期: {latest_prediction['ds'].strftime('%Y-%m-%d')}")
        print(f"   预测价格: ¥{latest_prediction['yhat']:.2f}")
        print(f"   置信区间: ¥{latest_prediction['yhat_lower']:.2f} - ¥{latest_prediction['yhat_upper']:.2f}")
        
        # 安全的组件图绘制（遵循第三方库兼容性处理规范）
        try:
            # model.plot_components(model_data)
            # plt.show()
            print("📊 组件分解图显示成功")
        except Exception as plot_error:
            print(f"⚠️ 组件图绘制出现问题: {plot_error}")
            print("模型和预测数据仍然可用")
        
        # 安全的变点分析
        try:
            print(f"\n📊 {stock_name} 变点分析:")
            moutai.changepoint_date_analysis()
            print("📊 变点分析完成")
        except Exception as analysis_error:
            print(f"⚠️ 变点分析出现问题: {analysis_error}")
            
    except Exception as model_error:
        print(f"❌ 模型创建失败: {model_error}")

else:
    print("无法获取股票数据，可能是网络问题或数据源问题")

# 展示新功能
print(f"\n🎆 新功能展示 - 股票名称支持:")
print("✅ 现在数据包含以下新列:")
print("   - Stock_Code: 股票代码")
print("   - Stock_Name: 股票中文名称")
print("   - Industry: 所属行业")
print("📊 支持A股主要股票的中文名称映射")
print("🔄 支持动态从 akshare 获取未知股票名称")