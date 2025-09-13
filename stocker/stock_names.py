"""
股票名称映射模块
支持A股股票代码到中文名称的映射
遵循A股股票代码支持规范
"""

import pandas as pd
from typing import Optional, Dict

# 导入完整的股票名称管理器
from .all_stock_names import (
    complete_stock_manager,
    get_complete_stock_name,
    get_complete_stock_industry,
    search_stocks,
    get_stocks_count,
    refresh_stock_names
)

# A股股票代码到名称的映射表
A_STOCK_NAMES = {
    # 银行股
    '000001': '平安银行',
    '000002': '万科A',
    '600000': '浦发银行',
    '600015': '华夏银行',
    '600016': '民生银行',
    '600036': '招商银行',
    '601166': '兴业银行',
    '601288': '农业银行',
    '601328': '交通银行',
    '601398': '工商银行',
    '601818': '光大银行',
    '601939': '建设银行',
    '002142': '宁波银行',
    
    # 白酒股
    '600519': '贵州茅台',
    '000858': '五粮液',
    '000596': '古井贡酒',
    '002304': '洋河股份',
    '000799': '酒鬼酒',
    '603369': '今世缘',
    '600779': '水井坊',
    '000568': '泸州老窖',
    '600702': '舍得酒业',
    
    # 科技股
    '000063': '中兴通讯',
    '000725': '京东方A',
    '002415': '海康威视',
    '300750': '宁德时代',
    '002594': '比亚迪',
    '600036': '招商银行',
    '000002': '万科A',
    '600519': '贵州茅台',
    
    # 医药股
    '000538': '云南白药',
    '002007': '华兰生物',
    '002422': '科伦药业',
    '600276': '恒瑞医药',
    '300015': '爱尔眼科',
    
    # 地产股
    '000002': '万科A',
    '000069': '华侨城A',
    '600048': '保利发展',
    '001979': '招商蛇口',
    
    # 消费股
    '000858': '五粮液',
    '600887': '伊利股份',
    '000895': '双汇发展',
    '002304': '洋河股份',
    '600519': '贵州茅台',
    
    # 新能源汽车
    '002594': '比亚迪',
    '300750': '宁德时代',
    '002460': '赣锋锂业',
    '300014': '亿纬锂能',
    
    # 其他知名股票
    '600050': '中国联通',
    '000063': '中兴通讯',
    '600741': '华域汽车',
    '601318': '中国平安',
    '600837': '海通证券',
    '000776': '广发证券',
}

# 行业分类映射
INDUSTRY_MAPPING = {
    # 银行
    '000001': '银行',
    '600000': '银行', 
    '600015': '银行',
    '600016': '银行',
    '600036': '银行',
    '601166': '银行',
    '601288': '银行',
    '601328': '银行',
    '601398': '银行',
    '601818': '银行',
    '601939': '银行',
    '002142': '银行',
    
    # 白酒
    '600519': '白酒',
    '000858': '白酒',
    '000596': '白酒',
    '002304': '白酒',
    '000799': '白酒',
    '603369': '白酒',
    '600779': '白酒',
    '000568': '白酒',
    '600702': '白酒',
    
    # 科技
    '000063': '通信设备',
    '000725': '电子',
    '002415': '安防设备',
    '300750': '新能源',
    '002594': '汽车',
    
    # 医药
    '000538': '医药',
    '002007': '医药',
    '002422': '医药',
    '600276': '医药',
    '300015': '医疗服务',
    
    # 地产
    '000002': '地产',
    '000069': '地产',
    '600048': '地产',
    '001979': '地产',
    
    # 金融
    '601318': '保险',
    '600837': '证券',
    '000776': '证券',
}


class StockNameManager:
    """股票名称管理器"""
    
    def __init__(self):
        self.name_cache = A_STOCK_NAMES.copy()
        self.industry_cache = INDUSTRY_MAPPING.copy()
    
    def get_stock_name(self, ticker: str) -> str:
        """
        获取股票中文名称
        
        Args:
            ticker: 股票代码
            
        Returns:
            str: 股票中文名称，如果找不到返回股票代码
        """
        ticker = ticker.strip().upper()
        
        # 去除可能的后缀
        if '.' in ticker:
            ticker = ticker.split('.')[0]
        
        # 查找缓存中的名称
        stock_name = self.name_cache.get(ticker)
        if stock_name:
            return stock_name
        
        # 如果没有找到，尝试从akshare动态获取
        try:
            stock_name = self._fetch_name_from_akshare(ticker)
            if stock_name:
                # 缓存结果
                self.name_cache[ticker] = stock_name
                return stock_name
        except:
            pass
        
        # 如果都没找到，返回一个格式化的默认名称
        return f"股票-{ticker}"
    
    def get_stock_industry(self, ticker: str) -> str:
        """
        获取股票所属行业
        
        Args:
            ticker: 股票代码
            
        Returns:
            str: 股票所属行业
        """
        ticker = ticker.strip().upper()
        if '.' in ticker:
            ticker = ticker.split('.')[0]
            
        return self.industry_cache.get(ticker, "其他")
    
    def _fetch_name_from_akshare(self, ticker: str) -> Optional[str]:
        """
        从akshare动态获取股票名称
        
        Args:
            ticker: 股票代码
            
        Returns:
            Optional[str]: 股票名称，如果获取失败返回None
        """
        try:
            import akshare as ak
            
            # 获取股票基本信息
            # 注意：这个API可能需要根据akshare版本调整
            stock_info = ak.stock_individual_info_em(symbol=ticker)
            
            if not stock_info.empty:
                # 查找包含股票名称的行
                name_row = stock_info[stock_info['item'] == '股票简称']
                if not name_row.empty:
                    return name_row['value'].iloc[0]
                    
        except Exception as e:
            print(f"从akshare获取股票名称失败: {e}")
            
        return None
    
    def batch_get_names(self, tickers: list) -> Dict[str, str]:
        """
        批量获取股票名称
        
        Args:
            tickers: 股票代码列表
            
        Returns:
            Dict[str, str]: 股票代码到名称的映射
        """
        result = {}
        for ticker in tickers:
            result[ticker] = self.get_stock_name(ticker)
        return result
    
    def add_stock_name(self, ticker: str, name: str, industry: str = "其他"):
        """
        添加新的股票名称映射
        
        Args:
            ticker: 股票代码
            name: 股票名称
            industry: 所属行业
        """
        ticker = ticker.strip().upper()
        if '.' in ticker:
            ticker = ticker.split('.')[0]
            
        self.name_cache[ticker] = name
        self.industry_cache[ticker] = industry
        print(f"✅ 已添加股票映射: {ticker} -> {name} ({industry})")


# 全局实例
stock_name_manager = StockNameManager()


def get_stock_name(ticker: str) -> str:
    """
    获取股票名称的简单接口
    支持所有A股股票名称查询
    """
    # 优先使用完整的股票名称管理器
    complete_name = get_complete_stock_name(ticker)
    if complete_name and not complete_name.startswith('股票-'):
        return complete_name
    
    # 如果完整管理器没有，使用原有的管理器
    return stock_name_manager.get_stock_name(ticker)


def get_stock_industry(ticker: str) -> str:
    """
    获取股票行业的简单接口
    支持所有A股股票行业查询
    """
    # 优先使用完整的股票名称管理器
    complete_industry = get_complete_stock_industry(ticker)
    if complete_industry and complete_industry != '其他':
        return complete_industry
    
    # 如果完整管理器没有，使用原有的管理器
    return stock_name_manager.get_stock_industry(ticker)


def add_stock_mapping(ticker: str, name: str, industry: str = "其他"):
    """添加股票映射的简单接口"""
    stock_name_manager.add_stock_name(ticker, name, industry)


# ===========================================
# 新增功能：支持所有A股股票名称查询
# ===========================================

def search_stocks_by_name(name_keyword: str):
    """
    根据股票名称关键词搜索股票
    
    Args:
        name_keyword: 股票名称关键词
        
    Returns:
        List[Dict]: 匹配的股票列表
    """
    return search_stocks(name_keyword)


def get_all_stocks_count():
    """
    获取系统中支持的股票总数
    
    Returns:
        int: 股票总数
    """
    return get_stocks_count()


def refresh_all_stock_names():
    """
    刷新所有股票名称缓存
    从 akshare 重新获取最新的股票名称数据
    """
    refresh_stock_names()


def get_stock_info(ticker: str) -> Dict[str, str]:
    """
    获取股票的完整信息
    
    Args:
        ticker: 股票代码
        
    Returns:
        Dict: 包含代码、名称、行业的字典
    """
    return {
        'code': ticker,
        'name': get_stock_name(ticker),
        'industry': get_stock_industry(ticker)
    }


def show_stock_coverage():
    """
    显示股票名称覆盖情况
    """
    built_in_count = len(A_STOCK_NAMES)
    total_count = get_all_stocks_count()
    
    print(f"📋 A股股票名称覆盖情况:")
    print(f"   ✅ 内置知名股票: {built_in_count} 只")
    print(f"   📊 缓存总股票数: {total_count} 只")
    print(f"   🎆 覆盖率: {(total_count/5000)*100:.1f}%") # 假设全市场约5000只股票
    print(f"   🔄 支持动态获取未知股票名称")