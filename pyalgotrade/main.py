from pyalgotrade import strategy
import akshare as ak
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.technical import ma


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__ma = ma.SMA(feed[instrument].getCloseDataSeries(),15)

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info( "%s  %s" %(bar.getClose(), self.__ma[-1]))




# 1. 获取 A 股日线数据
stock_code = "sh600519"  # 贵州茅台
df = ak.stock_zh_a_daily(
    symbol=stock_code,
    adjust="qfq"  # 前复权
)

# 2. 转换列名，适配 PyAlgoTrade
df = df.reset_index()  # 确保日期是普通列
df.rename(columns={
    'date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
df.to_csv('600519.csv', index=False)



feeds = quandlfeed.Feed()
feeds.addBarsFromCSV("orcl", "600519.csv")

# print(feeds)


myStrategy = MyStrategy(feeds, "orcl")
myStrategy.run()