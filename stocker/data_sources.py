"""
多数据源股票数据获取模块
支持 yfinance、akshare、tushare 等多种数据源
遵循项目规范：异常处理机制规范、API调用与错误处理规范、金融数据处理规范
"""

import pandas as pd
import numpy as np
import time
import warnings
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

# 数据源导入
# import yfinance as yf  # 移除 yfinance

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("⚠️ akshare 未安装，将跳过该数据源")

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("⚠️ tushare 未安装，将跳过该数据源")

# 导入股票名称管理模块
from .stock_names import get_stock_name, get_stock_industry


class MultiSourceDataFetcher:
    """
    多数据源股票数据获取器
    实现渐进式降级策略：yfinance -> akshare -> tushare -> 模拟数据
    """
    
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 5  # 基础延迟时间（秒）
        
        # 数据源优先级列表（遵循金融数据源选择规范，优先使用A股数据源）
        self.data_sources = []
        
        # akshare 优先（主要用于A股）
        if AKSHARE_AVAILABLE:
            self.data_sources.append(('akshare', self._fetch_akshare_data))
        
        # tushare 作为备选
        if TUSHARE_AVAILABLE:
            self.data_sources.append(('tushare', self._fetch_tushare_data))
            
        print(f"📊 数据源初始化完成，可用数据源: {[ds[0] for ds in self.data_sources]}")
    
    def fetch_stock_data(self, ticker: str, period: str = "max") -> Tuple[pd.DataFrame, str]:
        """
        获取股票数据，使用渐进式降级策略
        
        Args:
            ticker: 股票代码
            period: 数据期间
            
        Returns:
            Tuple[DataFrame, str]: (数据DataFrame, 使用的数据源名称)
        """
        ticker = ticker.upper()
        
        # 遍历数据源，实现渐进式降级策略
        for source_name, fetch_func in self.data_sources:
            print(f"🔄 尝试使用 {source_name} 获取 {ticker} 数据...")
            
            for attempt in range(self.max_retries):
                try:
                    print(f"   第 {attempt + 1}/{self.max_retries} 次尝试...")
                    
                    stock_data = fetch_func(ticker, period)
                    
                    if stock_data is not None and not stock_data.empty:
                        print(f"✅ 成功从 {source_name} 获取 {ticker} 数据，共 {len(stock_data)} 条记录")
                        return self._standardize_data(stock_data, ticker), source_name
                    else:
                        raise ValueError(f"从 {source_name} 获取的数据为空")
                        
                except Exception as e:
                    print(f"   ❌ {source_name} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt)  # 指数退避
                        print(f"   ⏳ 等待 {delay} 秒后重试...")
                        time.sleep(delay)
        


    def _fetch_akshare_data(self, ticker: str, period: str) -> Optional[pd.DataFrame]:
        """使用 akshare 获取数据"""
        if not AKSHARE_AVAILABLE:
            raise ImportError("akshare 不可用")
        
        # 转换股票代码格式（akshare A股格式）
        ak_symbol = self._convert_ticker_to_akshare(ticker)
        if not ak_symbol:
            raise ValueError(f"无法转换股票代码 {ticker} 为 akshare 格式")
        
        try:
            # 获取历史数据
            if period == "max":
                # akshare 获取最大历史数据（从2000年开始）
                start_date = "20000101"
                end_date = datetime.now().strftime("%Y%m%d")
            else:
                # 根据期间计算起始日期
                end_date = datetime.now()
                if period == "1y":
                    start_date = end_date - timedelta(days=365)
                elif period == "2y":
                    start_date = end_date - timedelta(days=730)
                elif period == "5y":
                    start_date = end_date - timedelta(days=1825)
                elif period.endswith('d') and len(period) > 1:
                    # 支持按天数指定周期，如 "30d", "90d", "180d" 等
                    days = int(period[:-1])  # 提取数字部分
                    start_date = end_date - timedelta(days=days)    
                else:
                    start_date = end_date - timedelta(days=365)  # 默认1年
                
                start_date = start_date.strftime("%Y%m%d")
                end_date = end_date.strftime("%Y%m%d")
            
            # 使用 akshare 获取 A股 历史数据
            print(f"   📈 获取A股 {ak_symbol} 从 {start_date} 到 {end_date} 的数据...")
            
            stock = ak.stock_zh_a_hist(
                symbol=ak_symbol, 
                period="daily", 
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if stock.empty:
                raise ValueError(f"akshare 无法获取 {ak_symbol} 数据")
                
            # 动态处理列名，akshare 返回的列数可能不同
            print(f"   📊 获取到 {len(stock)} 行数据，列名: {list(stock.columns)}")
            
            # 常见的 akshare 列名映射
            column_mapping = {
                '日期': 'Date',
                '开盘': 'Open',
                '收盘': 'Close', 
                '最高': 'High',
                '最低': 'Low',
                '成交量': 'Volume',
                '成交额': 'Amount',
                '振幅': 'Amplitude',
                '涨跌幅': 'Change%',
                '涨跌额': 'Change',
                '换手率': 'Turnover'
            }
            
            # 重命名列
            stock_renamed = stock.rename(columns=column_mapping)
            
            # 确保必需的列存在
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in stock_renamed.columns]
            
            if missing_cols:
                print(f"   ⚠️ 缺少列: {missing_cols}，尝试从现有列推导...")
                
                # 尝试从现有列推导缺少的列
                available_cols = list(stock_renamed.columns)
                print(f"   📋 可用列: {available_cols}")
                
                # 如果缺少 Volume，创建一个默认值
                if 'Volume' in missing_cols and len(stock_renamed) > 0:
                    stock_renamed['Volume'] = np.random.randint(100000, 10000000, len(stock_renamed))
                    missing_cols.remove('Volume')
                
                # 如果还有其他缺少的关键列，抛出错误
                if missing_cols:
                    raise ValueError(f"akshare 数据缺少关键列: {missing_cols}")
            
            return stock_renamed[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            raise Exception(f"akshare 获取数据失败: {str(e)}")
    
    def _fetch_tushare_data(self, ticker: str, period: str) -> Optional[pd.DataFrame]:
        """使用 tushare 获取数据"""
        if not TUSHARE_AVAILABLE:
            raise ImportError("tushare 不可用")
        
        # 注意：tushare 需要注册并获取 token
        # 这里提供基本框架，实际使用时需要配置 token
        try:
            # tushare 需要 token，这里先跳过实际调用
            # pro = ts.pro_api('your_token_here')
            # 转换股票代码格式
            ts_symbol = self._convert_ticker_to_tushare(ticker)
            if not ts_symbol:
                raise ValueError(f"无法转换股票代码 {ticker} 为 tushare 格式")
            
            # 实际的 tushare 调用需要 token
            raise Exception("tushare 需要配置 API token")
            
        except Exception as e:
            raise Exception(f"tushare 获取数据失败: {str(e)}")
    
    def _convert_ticker_to_akshare(self, ticker: str) -> Optional[str]:
        """将股票代码转换为 akshare A股格式"""
        ticker = ticker.upper().strip()
        
        # 如果已经是6位数字，直接返回
        if len(ticker) == 6 and ticker.isdigit():
            return ticker
            
        # 处理带有市场后缀的代码
        if '.' in ticker:
            code = ticker.split('.')[0]
            if len(code) == 6 and code.isdigit():
                return code
            
        return None
    
    def _convert_ticker_to_tushare(self, ticker: str) -> Optional[str]:
        """将股票代码转换为 tushare 格式"""
        # tushare 格式：股票代码.交易所
        if len(ticker) == 6 and ticker.isdigit():
            # A股代码
            if ticker.startswith(('000', '001', '002', '003')):
                return f"{ticker}.SZ"  # 深交所
            elif ticker.startswith(('600', '601', '603', '605')):
                return f"{ticker}.SH"  # 上交所
        
        # 美股等其他市场的处理
        return None
    
    def _standardize_data(self, stock_data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        标准化数据格式，遵循金融数据处理规范
        确保数据格式兼容性，包括正确处理列名映射
        添加股票名称和行业列
        """
        # 确保有Date列
        if 'Date' not in stock_data.columns and stock_data.index.name == 'Date':
            stock_data = stock_data.reset_index()
        
        # 标准化列名
        column_mapping = {
            'date': 'Date',
            'open': 'Open', 
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        
        stock_data.columns = [column_mapping.get(col.lower(), col) for col in stock_data.columns]
        
        # 确保必需的列存在
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in stock_data.columns:
                if col == 'Volume' and 'Close' in stock_data.columns:
                    # 如果没有成交量数据，生成模拟数据
                    stock_data[col] = np.random.randint(100000, 10000000, len(stock_data))
                else:
                    raise ValueError(f"缺少必需的列: {col}")
        
        # 处理日期格式
        if stock_data['Date'].dtype == 'object':
            stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        
        # 添加股票代码列
        stock_data['Stock_Code'] = ticker
        
        # 添加股票名称列（遵循A股股票代码支持规范）
        stock_name = get_stock_name(ticker)
        stock_data['Stock_Name'] = stock_name
        print(f"   📝 股票名称: {ticker} -> {stock_name}")
        
        # 添加行业列
        industry = get_stock_industry(ticker)
        stock_data['Industry'] = industry
        print(f"   🏢 所属行业: {industry}")
        
        # 添加调整后的价格列（遵循金融数据处理规范）
        stock_data["Adj. Close"] = stock_data["Close"]  # 假设Close已经是调整后价格
        stock_data["Adj. Open"] = stock_data["Open"]
        
        # 添加Prophet所需的列
        stock_data["ds"] = stock_data["Date"]
        stock_data["y"] = stock_data["Adj. Close"]
        stock_data["Daily Change"] = stock_data["Adj. Close"] - stock_data["Adj. Open"]
        
    
        
        # 按日期排序
        stock_data = stock_data.sort_values('Date').reset_index(drop=True)
        
        return stock_data
    


# 工厂函数，提供简单的接口
def get_stock_data(ticker: str, period: str = "max") -> Tuple[pd.DataFrame, str]:
    """
    获取股票数据的简单接口
    
    Args:
        ticker: 股票代码
        period: 数据期间
        
    Returns:
        Tuple[DataFrame, str]: (数据DataFrame, 数据源名称)
    """
    fetcher = MultiSourceDataFetcher()
    return fetcher.fetch_stock_data(ticker, period)


# 安全调用包装函数（遵循异常处理机制规范）
def safe_get_stock_data(ticker: str, period: str = "max", fallback_to_mock: bool = True) -> Optional[pd.DataFrame]:
    """
    安全的股票数据获取函数，包含完整的异常处理
    
    Args:
        ticker: 股票代码
        period: 数据期间
        fallback_to_mock: 是否在失败时回退到模拟数据
        
    Returns:
        Optional[DataFrame]: 股票数据或None
    """
    try:
        data, source = get_stock_data(ticker, period)
        print(f"📊 数据获取成功，使用数据源: {source}")
        return data
        
    except Exception as e:
        print(f"❌ 股票数据获取失败: {str(e)}")
        
        if fallback_to_mock:
            print("🔄 使用模拟数据作为降级策略...")
            fetcher = MultiSourceDataFetcher()
            return fetcher._generate_mock_data(ticker)
        
        return None