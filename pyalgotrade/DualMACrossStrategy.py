import re
from pyalgotrade import strategy
import akshare as ak
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import ma

from pyalgotrade import broker
import akshare as ak

from pyalgotrade.technical import ma
from pyalgotrade import plotter  # 修正导入语句
import matplotlib.pyplot as plt

# =============================
# 1. 获取 A 股数据并保存为 CSV
# =============================
stock_code = "sh600152"
df = ak.stock_zh_a_daily(symbol=stock_code, start_date='20240101',adjust="qfq")

df = df.reset_index()
df.rename(columns={
    'date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
df.to_csv('600152.csv', index=False)

# =============================
# 2. 定义策略：带完整交易回调
# =============================
class DualMACrossStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, short_window=5, long_window=20):
        super(DualMACrossStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__close_data = feed[instrument].getCloseDataSeries()
        self.__short_sma = ma.SMA(self.__close_data, short_window)
        self.__long_sma = ma.SMA(self.__close_data, long_window)
        
        self.__position = None
        self.__total_return = 0.0  # 跟踪总收益
        self.__initial_equity = self.getBroker().getEquity()  # 初始资金

        # 设置佣金（可选）
        # self.getBroker().setCommission(
        #     broker.backtesting.FixedPerTrade(5)  # 每笔交易 5 元手续费
        # )

    def getShortSMA(self):
        return self.__short_sma
    
    def getLongSMA(self):
        return self.__long_sma

    def onEnterOk(self, position):
        """买入单成交时触发"""
        exec_info = position.getEntryOrder().getExecutionInfo()
        self.info(f"✅ 买入成交 | 价格: ￥{exec_info.getPrice():.2f} | 数量: {exec_info.getQuantity()} 股")

    def onEnterCanceled(self, position):
        """买入单被取消时触发（如限价单未成交）"""
        order = position.getEntryOrder()
        # 修复：使用正确的属性和方法获取订单信息
        self.info(f"❌ 买入已取消 | 订单ID: {order.getId()} | 状态: {order.getState()}")

    def onExitOk(self, position):
        """卖出单成交时触发"""
        exec_info = position.getExitOrder().getExecutionInfo()
        self.info(f"✅ 卖出成交 | 价格: ￥{exec_info.getPrice():.2f} | 数量: {exec_info.getQuantity()} 股")
        
        # 计算本次交易的收益
        buy_price = position.getEntryOrder().getExecutionInfo().getPrice()
        sell_price = exec_info.getPrice()
        quantity = exec_info.getQuantity()
        trade_return = (sell_price - buy_price) * quantity
        
        # 更新总收益
        self.__total_return += trade_return
        self.info(f"💰 本次交易收益: ￥{trade_return:.2f} | 累计总收益: ￥{self.__total_return:.2f}")

    def onExitCanceled(self, position):
        """卖出单被取消时触发"""
        order = position.getExitOrder()
        # 修复：使用正确的属性和方法获取订单信息
        self.info(f"❌ 卖出已取消 | 订单ID: {order.getId()} | 状态: {order.getState()}")

    def onBars(self, bars):
        # 确保均线有足够的数据进行比较
        if (self.__short_sma[-1] is None or self.__long_sma[-1] is None or 
            self.__short_sma[-2] is None or self.__long_sma[-2] is None):
            return

        bar = bars[self.__instrument]
        current_price = bar.getClose()
        
        # 获取broker对象
        broker = self.getBroker()
        
        # 输出每日股票数据
        # self.info(f"📅 日期: {bar.getDateTime().date()} | "
        #           f"💰 收盘价: {current_price:.2f} | "
        #           f"📈 短期均线: {self.__short_sma[-1]:.2f} | "
        #           f"📊 长期均线: {self.__long_sma[-1]:.2f} | "
        #           f"📍 持仓状态: {'有' if self.__position and self.__position.isOpen() else '无'}")

        # 检查金叉（买入信号）
        # 修正逻辑：无论是否有持仓，都检查金叉信号
        if self.__short_sma[-2] <= self.__long_sma[-2] and self.__short_sma[-1] > self.__long_sma[-1]:
            # self.info(f"📈 金叉信号：短期均线 {self.__short_sma[-2]:.2f}->{self.__short_sma[-1]:.2f} 上穿长期均线 {self.__long_sma[-2]:.2f}->{self.__long_sma[-1]:.2f}")
            # 如果当前没有持仓，则买入
            if self.__position is None or not self.__position.isOpen():
                # 计算能买尽买的数量
                cash = broker.getCash()
                max_quantity = int(cash / current_price)  # 最大可购买数量
                
                if max_quantity > 0:
                    self.info(f"💰 执行买入操作 | 当前价格: {current_price:.2f} | 可用资金: {cash:.2f} | 买入数量: {max_quantity}")
                    self.__position = self.enterLong(self.__instrument, quantity=max_quantity, goodTillCanceled=True)
                else:
                    self.info(f"⚠️ 资金不足，无法买入 | 当前价格: {current_price:.2f} | 可用资金: {cash:.2f}")

        # 检查死叉（卖出信号）
        # 修正逻辑：无论是否有持仓，都检查死叉信号
        elif self.__short_sma[-2] >= self.__long_sma[-2] and self.__short_sma[-1] < self.__long_sma[-1]:
            # self.info(f"📉 死叉信号：短期均线 {self.__short_sma[-2]:.2f}->{self.__short_sma[-1]:.2f} 下穿长期均线 {self.__long_sma[-2]:.2f}->{self.__long_sma[-1]:.2f}")
            # 如果当前有持仓，则卖出
            if self.__position and self.__position.isOpen():
                # 全部卖出
                current_shares = broker.getShares(self.__instrument)
                self.info(f"💰 执行卖出操作 | 当前持仓: {current_shares} 股")
                self.__position.exitMarket()  # 使用正确的平仓方法
            

    def onFinish(self, bars):
        """策略结束时调用"""
        final_equity = self.getBroker().getEquity()
        total_return_pct = (final_equity - self.__initial_equity) / self.__initial_equity * 100
        self.info("=" * 50)
        self.info("📈 策略执行完成报告")
        self.info("=" * 50)
        self.info(f"初始资金: ￥{self.__initial_equity:.2f}")
        self.info(f"最终价值: ￥{final_equity:.2f}")
        self.info(f"总收益率: {total_return_pct:.2f}%")
        self.info(f"绝对收益: ￥{self.__total_return:.2f}")
        self.info("=" * 50)

# =============================
# 3. 运行策略
# =============================
feed = quandlfeed.Feed()
feed.addBarsFromCSV("600152", "600152.csv")  # 注意：instrument 名必须一致

my_strategy = DualMACrossStrategy(feed, "600152")
my_strategy.getBroker().setCash(1000000)  # 设置初始资金为10万元

# 创建收益率分析器
returnAnalyzer = returns.Returns()  # 修正参数
my_strategy.attachAnalyzer(returnAnalyzer)

# 创建策略绘图器
plt_plotter = plotter.StrategyPlotter(my_strategy)

# 添加收盘价和移动平均线到图表
plt_plotter.getInstrumentSubplot("600152").addDataSeries("Short SMA", my_strategy.getShortSMA())
plt_plotter.getInstrumentSubplot("600152").addDataSeries("Long SMA", my_strategy.getLongSMA())

# 添加收益率和累计收益率曲线
plt_plotter.getOrCreateSubplot("Returns").addDataSeries("Returns", returnAnalyzer.getReturns())
plt_plotter.getOrCreateSubplot("Cumulative Returns").addDataSeries("Cumulative Returns", returnAnalyzer.getCumulativeReturns())

# 运行策略
my_strategy.run()

# 绘制图表
plt_plotter.plot()

# 打印最终结果
print("Final portfolio value: $%.2f" % my_strategy.getBroker().getEquity())
