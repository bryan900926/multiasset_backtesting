import pandas as pd

class GetData: # enter the price column as close 
    def __init__(self, data_source, col_to_retreive): #file path for the data 
        df = pd.read_csv(data_source, parse_dates=['date'], index_col='date')
        self.data = df[col_to_retreive].dropna()

    def get_data(self, start_date):
        start_date = pd.Timestamp(start_date)
        return self.data[self.data.index == start_date].copy()