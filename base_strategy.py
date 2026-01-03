class BaseStrategy:
    def __init__(self, data):
        self.data = data
        self.signals = None
    
    def generate_signals(self):
        """Every strategy must create signals"""
        raise NotImplementedError("Each strategy needs its own signal logic")
    
    def get_latest_signal(self):
        """Returns the most recent signal strength"""
        return self.signals.iloc[-1]['signal']