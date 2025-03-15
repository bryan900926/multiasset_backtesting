import numpy as np

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