import pandas as pd

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