from stocker.stocker import Stocker
from strategy import Base


if __name__ == '__main__':
    # 创建一个Stocker实例
    strategy = Base('600152',period='1y')   
    
    print("📊 Base类初始化后的完整股票数据:")
    print("=" * 80)
    print(f"📋 数据维度: {strategy.stock.shape}")
    print(f"📊 所有列名: {list(strategy.stock.columns)}")
    
    # 遵循DataFrame输出规范：显示最近100行数据
    print("\n🔍 最近100行数据（所有列）:")
    print("-" * 80)
    # 使用to_string()方法显示所有列，遵循index=False规范
    print(strategy.stock.tail(100).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("🚀 正在执行交易策略...")
    strategy.strategy()
   
    strategy.display_results()
    t,p =strategy.p_t_test()
    #p小于5% 才有显著性
    print(f"\nt:{t},p:{p}")