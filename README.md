# Multi-Strategy-Trading-Bot-and-Backtester
A bot that allows user to backtest combinations of different strategies and see the outcome of these strategies on historical stock data. 


# Multi-Strategy Algorithmic Trading Bot

A Python-based algorithmic trading system that combines multiple technical analysis strategies to generate trading signals and backtest performance on historical stock data.

## 🎯 Overview

This trading bot implements a sophisticated multi-strategy approach to algorithmic trading, featuring:
- **4 Technical Indicators**: MA Crossover, MACD, RSI, and Bollinger Bands
- **Strategy Aggregation**: Combines multiple signals with customizable weights
- **Comprehensive Backtesting**: Realistic simulation with transaction costs and slippage
- **Performance Visualization**: Beautiful charts showing trades, equity curve, drawdown, and more

## 📊 Performance Highlights

Based on backtesting with optimized parameters:
- **Return**: ~130% over 5-year period (2020-2025 on AAPL)
- **Win Rate**: ~48%
- **Trades**: ~54 quality trades (selective trading approach)
- **Strategy**: Combines trend-following (MA + MACD) for balanced signals

## 🚀 Features

### Trading Strategies
1. **Moving Average Crossover** - Trend detection using fast (5-day) and slow (20-day) moving averages
2. **MACD** - Momentum and trend direction using exponential moving averages
3. **RSI** - Mean reversion signals based on overbought/oversold conditions
4. **Bollinger Bands** - Volatility-based trading signals

### Strategy Manager
- Combines signals from multiple strategies with weighted aggregation
- Configurable weights for each strategy
- Signal threshold filtering to reduce noise
- Modular design for easy strategy addition/removal

### Backtester
- Realistic position sizing (95% of available capital)
- Transaction costs (0.1% per trade)
- Comprehensive trade tracking
- Performance metrics:
  - Total return percentage
  - Maximum drawdown
  - Win rate
  - Average trade return
  - Sharpe ratio ready

### Visualization Suite
Six comprehensive charts showing:
1. Stock price with buy/sell signals
2. Portfolio equity curve over time
3. Drawdown analysis
4. Individual trade returns
5. Performance metrics summary
6. Monthly returns breakdown

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Required Libraries
```bash
pip install pandas
pip install yfinance
pip install matplotlib
pip install numpy
```

## 📁 Project Structure

```
trading-bot/
├── strategies/
│   ├── base_strategy.py       # Abstract base class for all strategies
│   ├── ma_crossover.py        # Moving Average Crossover strategy
│   ├── macd.py                # MACD strategy
│   ├── rsi.py                 # RSI strategy
│   └── bollinger_bands.py     # Bollinger Bands strategy
├── core/
│   ├── strategymanager.py     # Combines multiple strategies
│   └── backtester.py          # Backtesting engine
├── tests/
│   └──full_backteste_file.py # RUN TEST HERE
└── README.md
```

## 🎮 Usage

### Basic Example

```python
import pandas as pd
import yfinance as yf
from ma_crossover import MACrossover
from macd import MACD
from strategymanager import StrategyManager
from backtester import Backtester

# Download data
ticker = "AAPL"
data = yf.download(ticker, start="2020-01-01", end="2025-12-31")
data = data[["Close"]]

# Create strategies
ma = MACrossover(data, sma_window=5, lma_window=20)
macd = MACD(data, fast_period=8, slow_period=17, signal_period=7)

# Generate signals
ma.generate_signals()
macd.generate_signals()

# Align dates
common_dates = ma.signals.index.intersection(macd.signals.index)
ma.signals = ma.signals.loc[common_dates]
macd.signals = macd.signals.loc[common_dates]

# Create strategy manager
manager = StrategyManager([ma, macd], weights=[0.5, 0.5])

# Run backtest
backtest = Backtester(
    data=data.loc[common_dates],
    strategy_manager=manager,
    initial_balance=10000,
    threshold=0.15,
    position_size_pct=0.95,
    transaction_cost=0.001
)

final_balance, metrics = backtest.run()
backtest.print_results()
```

### Running with Visualization

```bash
python tests/backtest_with_viz.py
```

This will:
1. Download historical data
2. Generate trading signals
3. Run backtest simulation
4. Display comprehensive performance charts
5. Print detailed metrics

## ⚙️ Configuration

### Strategy Parameters

**MA Crossover:**
- `sma_window`: Short moving average period (default: 5)
- `lma_window`: Long moving average period (default: 20)

**MACD:**
- `fast_period`: Fast EMA period (default: 8)
- `slow_period`: Slow EMA period (default: 17)
- `signal_period`: Signal line period (default: 7)
- `threshold`: Signal strength threshold (default: 0.5)

**RSI:**
- `period`: RSI calculation period (default: 14)

**Bollinger Bands:**
- `sma_window`: Moving average period (default: 20)
- `num_std`: Number of standard deviations (default: 2)

### Backtester Parameters

- `initial_balance`: Starting capital (default: $10,000)
- `threshold`: Minimum signal strength to trade (default: 0.15)
- `position_size_pct`: Percentage of capital to use per trade (default: 0.95)
- `transaction_cost`: Commission per trade (default: 0.001 = 0.1%)

### Strategy Weights

Adjust weights in the `StrategyManager`:
```python
# Equal weighting
weights = [0.25, 0.25, 0.25, 0.25]

# Trend-focused (recommended)
weights = [0.5, 0.5]  # MA + MACD only

# Custom weighting
weights = [0.4, 0.3, 0.2, 0.1]  # MA, MACD, RSI, Bollinger
```


## 🔬 Testing on Different Stocks

The bot has been tested on:
- **AAPL**: 130% return (2020-2025)
- **NVDA**: 15% return (2025 only)
- **GOOGL**: 26% return (2025 only)

Performance varies by market conditions and stock volatility. Always backtest thoroughly before live trading.

## ⚠️ Important Disclaimers

1. **Past performance does not guarantee future results**
2. **This is for educational purposes only** - not financial advice
3. **Always test thoroughly** before using real money
4. **Markets can be irrational** - no strategy works 100% of the time
5. **Consider transaction costs** - they significantly impact profitability
6. **Slippage and real-world conditions** may differ from backtests

## 🚧 Known Limitations

- Backtester assumes perfect execution at close prices
- Does not account for liquidity constraints
- No stop-loss implementation (yet)
- Single-position system (no portfolio diversification)
- Does not handle gaps or halted trading
- Requires sufficient historical data for indicators

## 🛣️ Roadmap

Future enhancements planned:
- [ ] Stop-loss and take-profit orders
- [ ] Portfolio management (multiple positions)
- [ ] Walk-forward optimization
- [ ] Paper trading integration (live data)
- [ ] Machine learning signal enhancement
- [ ] Sentiment analysis integration
- [ ] Options trading strategies
- [ ] Risk-adjusted position sizing
- [ ] Real-time alert system

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional technical indicators
- Better risk management
- Performance optimizations
- Documentation improvements
- Bug fixes

## 📝 License

MIT License - feel free to use and modify for your own purposes.

## 👤 Author

Built as a learning project to explore algorithmic trading, technical analysis, and quantitative finance.

## 🙏 Acknowledgments

- Thanks to the yfinance library for easy data access
- Inspired by quantitative trading literature and research
- Built with guidance from the algorithmic trading community

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**⚠️ Risk Warning**: Trading involves substantial risk. This software is provided as-is with no guarantees. Always do your own research and never risk more than you can afford to lose.
