"""
完整A股股票名称获取模块
支持获取所有A股股票的中文名称和行业信息
遵循股票数据扩展与映射规范
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import os
import pickle
from datetime import datetime, timedelta

# 股票名称缓存文件路径
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'stock_names_cache.pkl')
CACHE_EXPIRE_DAYS = 7  # 缓存过期天数

class CompleteStockNameManager:
    """完整的A股股票名称管理器"""
    
    def __init__(self):
        self.stock_names = {}
        self.stock_industries = {}
        self.cache_date = None
        
        # 加载缓存
        self._load_cache()
        
        # 如果缓存为空或过期，重新获取
        if self._is_cache_expired():
            print("📥 股票名称缓存已过期或为空，正在获取最新数据...")
            self._fetch_all_stock_names()
    
    def _load_cache(self):
        """加载本地缓存"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.stock_names = cache_data.get('names', {})
                    self.stock_industries = cache_data.get('industries', {})
                    self.cache_date = cache_data.get('date', None)
                print(f"✅ 已加载股票名称缓存，包含 {len(self.stock_names)} 只股票")
        except Exception as e:
            print(f"⚠️ 加载缓存失败: {e}")
            self.stock_names = {}
            self.stock_industries = {}
            self.cache_date = None
    
    def _save_cache(self):
        """保存缓存到本地"""
        try:
            cache_data = {
                'names': self.stock_names,
                'industries': self.stock_industries,
                'date': datetime.now()
            }
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"💾 已保存股票名称缓存，包含 {len(self.stock_names)} 只股票")
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")
    
    def _is_cache_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self.cache_date:
            return True
        
        expire_date = self.cache_date + timedelta(days=CACHE_EXPIRE_DAYS)
        return datetime.now() > expire_date
    
    def _fetch_all_stock_names(self):
        """从akshare获取所有A股股票名称"""
        try:
            import akshare as ak
            
            print("🔄 正在从akshare获取所有A股股票信息...")
            
            # 获取A股股票列表
            # 沪深A股
            stock_list_methods = [
                ('沪深A股', lambda: ak.stock_info_a_code_name()),
                ('上证A股', lambda: ak.stock_zh_a_spot_em()[['代码', '名称']]),
            ]
            
            all_stocks = {}
            
            for method_name, method_func in stock_list_methods:
                try:
                    print(f"   📊 获取{method_name}股票列表...")
                    df = method_func()
                    
                    if not df.empty:
                        # 标准化列名
                        if 'code' in df.columns and 'name' in df.columns:
                            df = df.rename(columns={'code': '代码', 'name': '名称'})
                        elif '股票代码' in df.columns and '股票名称' in df.columns:
                            df = df.rename(columns={'股票代码': '代码', '股票名称': '名称'})
                        
                        # 确保有正确的列
                        if '代码' in df.columns and '名称' in df.columns:
                            for _, row in df.iterrows():
                                code = str(row['代码']).zfill(6)  # 确保6位数字
                                name = str(row['名称']).strip()
                                if code and name and code.isdigit():
                                    all_stocks[code] = name
                        
                        print(f"   ✅ {method_name}: 获取到 {len(df)} 只股票")
                    
                except Exception as e:
                    print(f"   ❌ 获取{method_name}失败: {e}")
                    continue
            
            # 如果上述方法都失败，尝试另一种方法
            if not all_stocks:
                try:
                    print("   🔄 尝试备用方法获取股票列表...")
                    # 获取实时行情数据（包含股票名称）
                    df = ak.stock_zh_a_spot_em()
                    if not df.empty and '代码' in df.columns and '名称' in df.columns:
                        for _, row in df.iterrows():
                            code = str(row['代码']).zfill(6)
                            name = str(row['名称']).strip()
                            if code and name and code.isdigit():
                                all_stocks[code] = name
                        print(f"   ✅ 备用方法: 获取到 {len(all_stocks)} 只股票")
                
                except Exception as e:
                    print(f"   ❌ 备用方法也失败: {e}")
            
            # 更新缓存
            if all_stocks:
                self.stock_names.update(all_stocks)
                
                # 为新股票设置默认行业
                for code in all_stocks:
                    if code not in self.stock_industries:
                        industry = self._guess_industry_by_code(code)
                        self.stock_industries[code] = industry
                
                self._save_cache()
                print(f"🎉 成功获取 {len(all_stocks)} 只A股股票名称!")
            else:
                print("❌ 未能获取到股票名称数据")
                
        except ImportError:
            print("❌ akshare 模块未安装，无法获取完整股票列表")
        except Exception as e:
            print(f"❌ 获取股票名称失败: {e}")
    
    def _guess_industry_by_code(self, code: str) -> str:
        """根据股票代码推测行业"""
        # 简单的行业推测逻辑
        if code.startswith('60'):
            return '沪市主板'
        elif code.startswith('00'):
            return '深市主板'
        elif code.startswith('30'):
            return '创业板'
        elif code.startswith('68'):
            return '科创板'
        else:
            return '其他'
    
    def get_stock_name(self, ticker: str) -> str:
        """
        获取股票中文名称
        
        Args:
            ticker: 股票代码
            
        Returns:
            str: 股票中文名称
        """
        ticker = ticker.strip().upper()
        
        # 去除可能的后缀
        if '.' in ticker:
            ticker = ticker.split('.')[0]
        
        # 确保是6位数字
        if ticker.isdigit():
            ticker = ticker.zfill(6)
        
        # 从缓存中查找
        name = self.stock_names.get(ticker)
        if name:
            return name
        
        # 如果缓存中没有，尝试实时获取
        try:
            name = self._fetch_single_stock_name(ticker)
            if name:
                self.stock_names[ticker] = name
                self.stock_industries[ticker] = self._guess_industry_by_code(ticker)
                return name
        except:
            pass
        
        # 如果都没有找到，返回格式化的默认名称
        return f"股票-{ticker}"
    
    def _fetch_single_stock_name(self, ticker: str) -> Optional[str]:
        """从akshare获取单只股票名称"""
        try:
            import akshare as ak
            
            # 尝试获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=ticker)
            
            if not stock_info.empty:
                # 查找包含股票名称的行
                name_row = stock_info[stock_info['item'] == '股票简称']
                if not name_row.empty:
                    return name_row['value'].iloc[0]
                    
        except Exception as e:
            print(f"从akshare获取股票 {ticker} 名称失败: {e}")
            
        return None
    
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
        
        if ticker.isdigit():
            ticker = ticker.zfill(6)
            
        return self.stock_industries.get(ticker, self._guess_industry_by_code(ticker))
    
    def search_stocks_by_name(self, name_keyword: str) -> List[Dict[str, str]]:
        """
        根据股票名称关键词搜索股票
        
        Args:
            name_keyword: 股票名称关键词
            
        Returns:
            List[Dict]: 匹配的股票列表
        """
        results = []
        
        for code, name in self.stock_names.items():
            if name_keyword in name:
                results.append({
                    'code': code,
                    'name': name,
                    'industry': self.get_stock_industry(code)
                })
        
        return results
    
    def get_all_stocks_count(self) -> int:
        """获取缓存中的股票总数"""
        return len(self.stock_names)
    
    def refresh_cache(self):
        """强制刷新缓存"""
        print("🔄 强制刷新股票名称缓存...")
        self.stock_names = {}
        self.stock_industries = {}
        self.cache_date = None
        self._fetch_all_stock_names()


# 全局实例
complete_stock_manager = CompleteStockNameManager()


def get_complete_stock_name(ticker: str) -> str:
    """获取完整股票名称的简单接口"""
    return complete_stock_manager.get_stock_name(ticker)


def get_complete_stock_industry(ticker: str) -> str:
    """获取股票行业的简单接口"""
    return complete_stock_manager.get_stock_industry(ticker)


def search_stocks(name_keyword: str) -> List[Dict[str, str]]:
    """搜索股票的简单接口"""
    return complete_stock_manager.search_stocks_by_name(name_keyword)


def get_stocks_count() -> int:
    """获取股票总数的简单接口"""
    return complete_stock_manager.get_all_stocks_count()


def refresh_stock_names():
    """刷新股票名称缓存的简单接口"""
    complete_stock_manager.refresh_cache()