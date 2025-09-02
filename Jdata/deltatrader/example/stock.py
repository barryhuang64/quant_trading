#!/usr/bin/env python
# encoding: utf-8
'''
@author: DeltaF
@software: pycharm
@file: stock.py
@time: 2021/3/5 02:08
@desc: 获取价格，并且计算涨跌幅
'''

import sys
import os

# 添加父目录到Python路径，以便导入data模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import data.stock as st

# 获取平安银行的行情数据（日K）- 使用账号权限允许的日期范围
data = st.get_single_price('000001.XSHE', 'daily', '2024-05-25', '2024-06-01')
# print(data)

# 计算涨跌幅，验证准确性
# data = st.calculate_change_pct(data)
# print(data)  # 多了一列close_pct

# 获取周K
data = st.transfer_price_freq(data, 'w')
print(data)

# 计算涨跌幅，验证准确性
data = st.calculate_change_pct(data)
print(data)  # 多了一列close_pct
