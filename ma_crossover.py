from base_strategy import BaseStrategy


class MACrossover(BaseStrategy):
    def __init__(self, data, lma_window=20, sma_window = 5):
        super().__init__(data)
        self.sma_window = sma_window
        self.lma_window = lma_window

    def generate_signals(self):
        ds = self.data.copy()
        
        #calculate moving averages 
        ds["SMA"] = ds["Close"].rolling(window=self.sma_window).mean()
        ds["LMA"] = ds["Close"].rolling(window=self.lma_window).mean()
        ds.dropna(inplace=True)

        #calc differences
        ds["ma_diff_pct"] = (ds["SMA"]-ds["LMA"]) / ds["LMA"]
        #generate signal 
        ds["signal"] = (ds["ma_diff_pct"] / 0.05).clip(-1.0, 1.0)
        ds.dropna(inplace=True)
        
        self.signals = ds  
        return ds         
    
   
