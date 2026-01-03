from base_strategy import BaseStrategy

class MACD(BaseStrategy):
    def __init__(self, data, fast_period=8, slow_period=17, signal_period=7, threshold=1.0):
        super().__init__(data)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.threshold = threshold
        

    def generate_signals(self):

        ds = self.data.copy()

        ds["ema_fast"] = ds["Close"].ewm(span=self.fast_period, adjust=False).mean()
        ds["ema_slow"] = ds["Close"].ewm(span=self.slow_period, adjust=False).mean()
        ds["macd_line"] = ds["ema_fast"] - ds["ema_slow"]
        ds["signal_line"] = ds["macd_line"].ewm(span=self.signal_period, adjust=False).mean()
        ds["histogram"] = ds["macd_line"] - ds["signal_line"]

        ds["signal"] = (ds["histogram"]) / self.threshold

        ds["signal"] = ds["signal"].clip(-1.0, 1.0)
        ds.dropna(inplace=True)

        self.signals = ds
        return ds
    

