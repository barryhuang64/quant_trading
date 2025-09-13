from stocker.stocker import Stocker
from strategy import Base


if __name__ == '__main__':
    # 创建一个Stocker实例
    strategy = Base('600152',period='2y')   
    strategy.strategy()
    strategy.display_results()
    t,p =strategy.p_t_test()
    print(f"t:{t},p:{p}")