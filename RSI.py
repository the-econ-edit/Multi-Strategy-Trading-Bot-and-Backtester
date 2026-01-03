from base_strategy import BaseStrategy

class RSI(BaseStrategy):
    def __init__(self, data, period=14, oversold=30, overbought=70):
        super().__init__(data)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self):

        ds = self.data.copy()

        delta = ds["Close"].diff()

        gain = (delta.where(delta > 0,0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0,0)).rolling(window=self.period).mean()

        relative_strength = gain / loss

        ds["RSI"] = 100 - (100/ (1 + relative_strength))



        ds["signal"] = (50 - ds["RSI"]) / 50  # Maps 0-100 to +1 to -1
      
    



        ds["signal"] = ds["signal"].clip(-1.0, 1.0)
        ds.dropna(inplace=True)
        self.signals = ds
        return ds


