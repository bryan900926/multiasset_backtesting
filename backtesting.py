import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

class GetData: # enter the price column as close 
    def __init__(self, data_source, col_to_retreive): #file path for the data 
        df = pd.read_csv(data_source, parse_dates=['date'], index_col='date')
        self.data = df[col_to_retreive].dropna()

    def get_data(self, start_date):
        start_date = pd.Timestamp(start_date)
        return self.data[self.data.index == start_date].copy()
        
class ranking_strategy:
    def __init__(self, data, factor, threshold, get_lowest):
        self.data = data
        self.factor = factor 
        self.threshold = threshold
        self.get_low_quantile = get_lowest

    def generate_signal(self):
        threshold = self.data[self.factor].quantile(self.threshold)
        if not self.get_low_quantile:   
           self.data['signal'] = (self.data[self.factor] >= threshold).astype(int)
        else:
           self.data['signal'] = (self.data[self.factor] <= threshold).astype(int)
        # print(self.data[self.data['signal'] == 1])
        return self.data
    
class random_strategy:
    def __init__(self,data):
        self.data = data

    def generate_signal(self, factor, threshold):
        self.data['signal'] = np.random.choice([0, 1], size=len(self.data))
        return self.data

class PortfolioManager:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.positions = {} # pos[ticker] = [timestamp, price, shares]
        self.trading_engine = ExecutionEngine()

    def update_portfolio(self, date, ticker, signal, price, output_order):
        if signal == 1:  
            if ticker not in self.positions:
               self.positions[ticker] = [date, price, 0]  # Initialize if not held
            else:
               self.positions[ticker][0] = date  # Initialize if not held
               self.positions[ticker][1] = price  # Initialize if not held

        elif signal == 0 and ticker in self.positions:  # Sell
            shares_held = self.positions[ticker][2]
            selling_price = self.trading_engine.execute_order(price, 0)
            selling_value = shares_held * selling_price
            self.cash += selling_value
            del self.positions[ticker]  

    def adjust_portfolio(self, output_order): #equally weighted
        num_positions = len(self.positions)
        if num_positions == 0:
            return 
        target_allocation = (self.get_portfolio_value() + self.cash) // num_positions

        for ticker in self.positions:
              current_price = self.positions[ticker][1]
              current_shares = self.positions[ticker][2]
              target_shares = target_allocation // current_price
  
              if current_shares > target_shares:
                  shares_to_sell = current_shares - target_shares
                  trade_price = self.trading_engine.execute_order(current_price, 0)
                  trading_value = shares_to_sell * trade_price
  
                  self.cash += trading_value
                  self.positions[ticker][2] -= shares_to_sell

        for ticker in self.positions:
            current_price = self.positions[ticker][1]
            current_shares = self.positions[ticker][2]
            target_shares = target_allocation / current_price

            if current_shares < target_shares: 
                shares_to_buy = target_shares - current_shares   
                trading_cost = shares_to_buy * self.trading_engine.execute_order(price = current_price, signal = 1)
                if trading_cost <= self.cash:  # Check if enough cash is available
                    self.cash -= trading_cost
                    self.positions[ticker][2] += shares_to_buy

    def get_portfolio_value(self):
        return sum(self.positions[ticker][1] * self.positions[ticker][2] for ticker in self.positions)
    
class ExecutionEngine:
    def __init__(self, slippage=0.01):
        self.slippage = slippage

    def execute_order(self, price, signal):
        return price * (1 + self.slippage) if signal == 1 else price * (1 - self.slippage)
    
    def log_order(price, signal, company, transaction_price):    
        action = "Buying" if signal == 1 else "Selling"
        print(f"{action} {company} at {transaction_price:.2f} with slippage.")

class Backtest:
    def __init__(self, trading_data, strategy, portfolio_manager, execution_engine):
        self.data_handler = trading_data
        self.strategy = strategy
        self.pm = portfolio_manager
        self.execution_engine = execution_engine
        self.past_value = []
        self.past_date = []
        self.market_idx = []
   
    def run(self, start_date, output_order = False):
        data = self.data_handler.get_data(start_date)
        mrk_idx = None
        if not len(data):
            print(f"no trading activity at {start_date}")
            return 
        self.strategy.data = data
        data_with_signal = self.strategy.generate_signal()
        # print(data_with_signal)
        for date, row in data_with_signal.iterrows():
            price = row['close']
            signal = row['signal']
            ticker = row['ticker']
            #self, date, ticker, signal, price, output_order
            self.pm.update_portfolio(date, ticker, signal, price, output_order)

        self.pm.adjust_portfolio(output_order)
        self.past_date.append(start_date)
        self.past_value.append(self.pm.cash + self.pm.get_portfolio_value())
        self.market_idx.append(row["close_tai_idx"])

class PerformanceMetrics:
    @staticmethod
    def calculate_returns(dates, portfolio_values, market_idx = []):
        if len(portfolio_values) < 2:
            return None  # Not enough data
    
        dates = pd.to_datetime(dates)
        df = pd.DataFrame({'Date': dates, 'Portfolio_Value': portfolio_values})
        df.set_index('Date', inplace=True)

        df['Return'] = df['Portfolio_Value'].pct_change()
        df['Days_Diff'] = df.index.to_series().diff().dt.days
        df['Annualized_Return'] = (1 + df['Return']) ** (365 / df['Days_Diff']) - 1

        plt.figure(figsize=(10, 5))
   
        if len(market_idx):
           df['market_idx'] = market_idx 
           df['Market_Return'] = df['market_idx'].pct_change()
           df['Annualized_Market_Return'] = (1 + df['Market_Return']) ** (365 / df['Days_Diff']) - 1
           plt.plot(df.index, 100 * df['Annualized_Market_Return'], label='Annualized Market Return %', color='red')
   
        plt.plot(df.index, 100 * df['Annualized_stratgy_Return'], label='Annualized Return %', color='blue')
        plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
        plt.xlabel("Date")
        plt.ylabel("Annualized Return %")
        plt.title("Annualized Return Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()  
        return df

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
        excess_returns = returns - risk_free_rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualize
        return sharpe_ratio

    @staticmethod
    def calculate_max_drawdown(portfolio_values):
        cumulative = portfolio_values.cummax()
        drawdown = (portfolio_values - cumulative) / cumulative
        max_drawdown = drawdown.min()
        return max_drawdown
    
    @staticmethod
    def calculate_position_value(timestamps, portfolio_values):
        plt.figure(figsize=(8, 5))
        plt.plot(timestamps, portfolio_values, marker='o', linestyle='-')
        plt.xlabel("Timestamp")
        plt.ylabel("Value")
        plt.title("Timestamp vs Value")
        plt.grid(True)
        plt.show()          

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
for time_idx in sorted(set(Data.data.index))[50:]:
    testing.run(time_idx, output_order = False)

a = PerformanceMetrics.calculate_returns(testing.past_date, testing.past_value, testing.market_idx)
# pd.set_option('display.max_rows', None)
# print(a)
