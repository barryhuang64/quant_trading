from stocker.stocker import Stocker
from strategy import Base


if __name__ == '__main__':
    # 创建一个Stocker实例
    strategy = Base('600152')   
    strategy.strategy()
    strategy.display_results()