#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票列表获取模块

该模块提供获取A股所有股票列表的功能，包括：
- 获取完整的A股股票代码和名称
- 按行业分类展示股票
- 搜索指定关键词的股票
- 显示股票统计信息

Author: Qoder
Date: 2025-09-13
"""

import sys
import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional
from strategy import Base


# 导入股票名称管理模块（遵循A股股票数据处理规范）
import stocker
from stocker.CompleteStockNameManager import (
    CompleteStockNameManager,
    complete_stock_manager,
    get_complete_stock_name,
    get_complete_stock_industry,
    search_stocks,
    get_stocks_count,
    refresh_stock_names
)
from stocker.stock_names import get_stock_name, get_stock_industry


if __name__ == '__main__':
    all_stock = CompleteStockNameManager().stock_names.keys()
    for stock_id in all_stock:
 
        stock =  Base(stock_id, period='1y').stock 
        
        stock = stock.set_index('Date')

        stock_month = stock.resample('M').last()
        print(stock_month.tail(100).to_string(index=False)) 

        # print(stock.tail(100).to_string(index=False))  # pyright: ignore[reportAttributeAccessIssue]
        exit()