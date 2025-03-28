import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from Get_data import GetData
from strategy import random_strategy, ranking_strategy
from Performance_metric import PerformanceMetrics
from backtesting import Backtest
from trading_engine import ExecutionEngine
from Portfolio import PortfolioManager


df = pd.read_csv(r'C:\Users\bryan\OneDrive\桌面\python\tsa\merge_df.csv')
Data = GetData(r'C:\Users\bryan\OneDrive\桌面\python\tsa\merge_df.csv', ['marketcap', 
                                                                       'close', 
                                                                       'ticker',
                                                                       'close_tai_idx'])
testing = Backtest(Data, 
                   ranking_strategy(data = None, factor = 'marketcap', threshold = 0.1, get_lowest = True), 
                   PortfolioManager(initial_cash = 100000), 
                   ExecutionEngine(slippage = 0.01))
# # print(Data.data)
for time_idx in sorted(set(Data.data.index)):
    testing.run(time_idx, output_order = False)

return_df = PerformanceMetrics.calculate_returns(testing.past_date, testing.past_value, testing.market_idx)
PerformanceMetrics.calculate_sharpe_ratio(return_df)
# pd.set_option('display.max_rows', None)
# print(a)
