from trading_egine import ExecutionEngine

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