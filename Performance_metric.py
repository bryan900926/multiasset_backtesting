import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

class PerformanceMetrics:
    @staticmethod
    def calculate_returns(dates, portfolio_values, market_idx = []):
        if len(portfolio_values) < 2:
            print("data sample is not enough")
            return None  # Not enough data
    
        dates = pd.to_datetime(dates)
        df = pd.DataFrame({'Date': dates, 'Portfolio_Value': portfolio_values})
        df.set_index('Date', inplace=True)

        df['Return'] = df['Portfolio_Value'].pct_change()
        df['Days_Diff'] = df.index.to_series().diff().dt.days
        df["Annualized_stratgy_Return"] = (1 + df['Return']) ** (365 / df['Days_Diff']) - 1

        plt.figure(figsize=(10, 5))
   
        # plt.plot(df.index, 100 * df['Annualized_stratgy_Return'], label='Annualized Return %', color='blue')
        
        if len(market_idx):
           df['market_idx'] = market_idx 
           df['Market_Return'] = df['market_idx'].pct_change()
           df['Annualized_Market_Return'] = (1 + df['Market_Return']) ** (365 / df['Days_Diff']) - 1
           df['excess_return'] = df["Annualized_stratgy_Return"] - df["Annualized_Market_Return"]
        #    plt.plot(df.index, 100 * df['Annualized_Market_Return'], label='Annualized Market Return %', color='red')
           plt.plot(df.index, 100 * df['excess_return'], label='excess_return', color='red')
   
        plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
        plt.xlabel("Date")
        plt.ylabel("Annualized Return %")
        plt.title("Annualized Return Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()  

        return df

    @staticmethod
    def calculate_sharpe_ratio(df, risk_free_rate = 0.01, window = 50):
        df["Rolling Mean Return"] = df['Annualized_Market_Return'].rolling(window).mean() - risk_free_rate
        df["Rolling Volatility"] = df['Annualized_Market_Return'].rolling(window).std()
        df["Sharpe Ratio"] = df["Rolling Mean Return"] / df["Rolling Volatility"]
        df = df.dropna()
        df["Sharpe Ratio"].plot(title="Rolling Sharpe Ratio", figsize=(12, 6))
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Sharpe Ratio")
        plt.grid(True)
        plt.show()

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
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Portfolio values")
        plt.grid(True)
        plt.show()          