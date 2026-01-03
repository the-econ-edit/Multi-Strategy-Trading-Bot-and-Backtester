import pandas as pd
import yfinance as yf
from ma_crossover import MACrossover
from MACD import MACD
from bollinger_bands import BollingerBands
from RSI import RSI
from strategymanager import StrategyManager
from backtester import Backtester



ticker = "AAPL"
start = "2020-01-01"
end = "2025-12-28"
data = yf.download(ticker, start=start, end=end)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]
data = data[["Close"]]
data.dropna(inplace=True)


# Fix MultiIndex columns issue
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

# Keep only Close column
data = data[["Close"]]
data.dropna(inplace=True)

ma = MACrossover(data, sma_window=5, lma_window=20) 
macd = MACD(data, fast_period=8, slow_period=17, signal_period=7, threshold=0.5) 
rsi = RSI(data, period=14, oversold=30, overbought=70)
bb = BollingerBands(data, sma_window=20)

ma.generate_signals()
macd.generate_signals()


common_dates = ma.signals.index.intersection(macd.signals.index)
ma.signals = ma.signals.loc[common_dates]
macd.signals = macd.signals.loc[common_dates]

# CHANGE STRATEGIES HERE
strategies = [ma, macd]
weights = [0.5, 0.5]

# Create manager
manager = StrategyManager(strategies, weights) 

manager.run_all_strategies()

# Run backtest with ONLY common dates
backtest = Backtester(
    data=data.loc[common_dates],  # ← Only common dates!
    strategy_manager=manager,
    initial_balance=1000,
    threshold=0.15,
    position_size_pct=0.95,
    transaction_cost=0.001
)

metrics = backtest.run()
backtest.print_results()
# ============================================================================
# VISUALIZATION - 
# ============================================================================
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(16, 13))  # Made taller
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3, top=0.96, bottom=0.05)  # More space

dates = [point['date'] for point in backtest.equity_curve]
equity = [point['equity'] for point in backtest.equity_curve]
prices = data.loc[common_dates, 'Close']

buy_trades = [t for t in backtest.trade_history if t['action'] == 'BUY']
sell_trades = [t for t in backtest.trade_history if 'SELL' in t['action']]
buy_dates = [t['date'] for t in buy_trades]
buy_prices = [t['price'] for t in buy_trades]
sell_dates = [t['date'] for t in sell_trades]
sell_prices = [t['price'] for t in sell_trades]

# Plot 1: Price with signals
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(prices.index, prices.values, label=f'{ticker} Price', color='blue', alpha=0.7, linewidth=2)
ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='Buy', zorder=5)
ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='Sell', zorder=5)
ax1.set_title(f'{ticker} Price with Trading Signals', fontsize=14, fontweight='bold', pad=10)
ax1.set_ylabel('Price ($)', fontsize=12)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# Plot 2: Equity curve
ax2 = fig.add_subplot(gs[1, :])
ax2.plot(dates, equity, label='Portfolio Value', color='green', linewidth=2)
ax2.axhline(y=backtest.initial_balance, color='gray', linestyle='--', alpha=0.5, label='Initial Balance')
ax2.set_title('Portfolio Equity Curve', fontsize=14, fontweight='bold', pad=10)
ax2.set_ylabel('Portfolio Value ($)', fontsize=12)
ax2.legend(loc='best')
ax2.grid(True, alpha=0.3)

# Plot 3: Drawdown
ax3 = fig.add_subplot(gs[2, 0])
peak = backtest.initial_balance
drawdowns = []
for point in backtest.equity_curve:
    if point['equity'] > peak:
        peak = point['equity']
    dd = (peak - point['equity']) / peak * 100
    drawdowns.append(dd)
ax3.fill_between(dates, 0, drawdowns, color='red', alpha=0.3)
ax3.plot(dates, drawdowns, color='red', linewidth=1)
ax3.set_title('Drawdown Over Time', fontsize=12, fontweight='bold', pad=10)
ax3.set_ylabel('Drawdown (%)', fontsize=10)
ax3.set_xlabel('Date', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.invert_yaxis()

# Plot 4: Trade returns
ax4 = fig.add_subplot(gs[2, 1])
profit_pcts = [t['profit_pct'] for t in sell_trades]
colors = ['green' if p > 0 else 'red' for p in profit_pcts]
ax4.bar(range(len(profit_pcts)), profit_pcts, color=colors, alpha=0.6)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax4.set_title('Individual Trade Returns', fontsize=12, fontweight='bold', pad=10)
ax4.set_ylabel('Return (%)', fontsize=10)
ax4.set_xlabel('Trade Number', fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

# Plot 5: Metrics panel - COMPACT
ax5 = fig.add_subplot(gs[3, 0])
ax5.axis('off')
final_bal = backtest.cash
total_ret = (final_bal - backtest.initial_balance) / backtest.initial_balance * 100
sell_only = [t for t in backtest.trade_history if 'SELL' in t['action']]
num_trades = len(sell_only)
winners = len([t for t in sell_only if t.get('profit', 0) > 0])
win_rate = (winners / num_trades * 100) if num_trades > 0 else 0
avg_ret = sum(t.get('profit_pct', 0) for t in sell_only) / num_trades if num_trades > 0 else 0
max_dd = backtest.calc_max_drawdown()

metrics_text = f"""PERFORMANCE
Initial:  ${backtest.initial_balance:,.0f}
Final:    ${final_bal:,.0f}
Return:   {total_ret:.1f}%
Max DD:   {max_dd:.1f}%

TRADING
Trades:   {num_trades}
Winners:  {winners}
Win Rate: {win_rate:.1f}%
Avg:      {avg_ret:.1f}%"""

ax5.text(0.1, 0.85, metrics_text, transform=ax5.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

# Plot 6: Monthly returns
ax6 = fig.add_subplot(gs[3, 1])
equity_df = pd.DataFrame(backtest.equity_curve)
equity_df['date'] = pd.to_datetime(equity_df['date'])
equity_df.set_index('date', inplace=True)
monthly_equity = equity_df['equity'].resample('M').last()
monthly_returns = monthly_equity.pct_change() * 100
colors_monthly = ['green' if r > 0 else 'red' for r in monthly_returns.dropna()]
ax6.bar(range(len(monthly_returns.dropna())), monthly_returns.dropna(), color=colors_monthly, alpha=0.6)
ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax6.set_title('Monthly Returns', fontsize=12, fontweight='bold', pad=10)
ax6.set_ylabel('Return (%)', fontsize=10)
ax6.set_xlabel('Month', fontsize=10)
ax6.grid(True, alpha=0.3, axis='y')
month_labels = [d.strftime('%b %y') for d in monthly_returns.dropna().index]
ax6.set_xticks(range(len(month_labels)))
ax6.set_xticklabels(month_labels, rotation=45, ha='right', fontsize=9)

fig.suptitle(f'Trading Strategy Backtest - {ticker}', fontsize=16, fontweight='bold')
plt.show()