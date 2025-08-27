# setup.py
from setuptools import setup, find_packages

setup(
    name="Data_Analysis",
    version="0.1.0",
    description="My data analysis library",
    packages=find_packages(),  # 自动发现 Data_Analysis 包
    # install_requires=[       # 如果你用了第三方库，比如：
    #     "pandas",
    #     "numpy",
    # ],
)