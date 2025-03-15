class ExecutionEngine:
    def __init__(self, slippage=0.01):
        self.slippage = slippage

    def execute_order(self, price, signal):
        return price * (1 + self.slippage) if signal == 1 else price * (1 - self.slippage)
    
    def log_order(price, signal, company, transaction_price):    
        action = "Buying" if signal == 1 else "Selling"
        print(f"{action} {company} at {transaction_price:.2f} with slippage.")
