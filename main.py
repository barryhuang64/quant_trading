import sys
import os
import matplotlib.pyplot as plt

# 使用完整包路径导入（遵循标准导入方式规范，支持IDE跳转）
from Data_Analysis.stocker import Stocker

# 可以继续添加其他导入  


microsoft = Stocker('603906')

# 检查是否成功获取数据
if hasattr(microsoft, 'stock'):
    microsoft_history = microsoft.stock
    print("✅ 成功获取股票数据")
    print(microsoft_history.tail())

    try:
        # 创建预测模型（遵循API调用与错误处理规范）
        model, model_data = microsoft.create_prophet_model(days=30)
        print("✅ Prophet模型创建成功")

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
            microsoft.changepoint_date_analysis()
            print("📊 变点分析完成")
        except Exception as analysis_error:
            print(f"⚠️ 变点分析出现问题: {analysis_error}")

    except Exception as model_error:
        print(f"❌ 模型创建失败: {model_error}")

else:
    print("无法获取股票数据，可能是 API 密钥问题或网络问题")
