from stocker.stocker import Stocker
from strategy import Base


if __name__ == '__main__':
    # 创建一个Stocker实例
    strategy = Base('600152',period='1y')   
 
    print(strategy.stock.tail(100).to_string(index=False))
    
】
    strategy.strategy()
   
    strategy.display_results()
    t,p =strategy.p_t_test()
    #p小于5% 才有显著性
    print(f"\nt:{t},p:{p}")