from base_strategy import BaseStrategy

class BollingerBands(BaseStrategy):
    def __init__(self, data, sma_window=20):
        super().__init__(data)
        self.sma_window = sma_window
        

    def generate_signals(self):

        ds = self.data.copy()

        ds["middle_band"] = ds["Close"].rolling(window=self.sma_window).mean()

        ds["std_dev"] = ds["Close"].rolling(window=self.sma_window).std()

        ds["upper_band"] = ds["middle_band"] + ds["std_dev"] * 2

        ds["lower_band"] = ds["middle_band"] - ds["std_dev"] * 2
 


        ds["signal"] = 0.0
 
        ds["band_width"] = (ds["upper_band"] - ds["lower_band"])
        ds["price_position"] = ds["Close"] - ds["middle_band"]
        ds["signal"] = -(ds["price_position"] / (ds["band_width"] / 2))

    
        ds["signal"] = ds["signal"].clip(-1.0, 1.0)
        ds.dropna(inplace=True)

    
        self.signals = ds
        return ds


