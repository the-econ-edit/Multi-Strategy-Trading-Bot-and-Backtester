import pandas as pd
import yfinance as yf
from ma_crossover import MACrossover
from MACD import MACD
from bollinger_bands import BollingerBands
from RSI import RSI
from strategymanager import StrategyManager


class Backtester:

    def __init__(self, data, strategy_manager, initial_balance=10000, threshold=0.15, position_size_pct=0.95, transaction_cost=0.001):

        self.data = data
        self.strategy_manager = strategy_manager
        self.initial_balance = initial_balance
        self.threshold = threshold
        self.position_size_pct = position_size_pct
        self.transaction_cost = transaction_cost

        self.cash = initial_balance
        self.shares = 0
        self.position = 0  # 0 = not holding, 1 = holding
        self.entry_price = None

        # Tracking
        self.trade_history = []
        self.equity_curve = []
       


    def run(self):
        for date in self.data.index:
            current_price = self.data.loc[date, "Close"]
            signal = self.strategy_manager.get_combined_signal(date)

            current_equity = self.cash + self.shares * current_price
            self.equity_curve.append({'date': date, 'equity': current_equity})


            if signal > self.threshold and self.position == 0:
                available_cash = self.cash * self.position_size_pct
                shares_to_buy = int(available_cash // current_price)

                if shares_to_buy > 0:
                    cost_before_fees = shares_to_buy * current_price
                    transaction_fee = cost_before_fees * self.transaction_cost
                    total_cost = cost_before_fees + transaction_fee

                    self.position = 1
                    self.shares = shares_to_buy
                    self.cash -= total_cost
                    self.entry_price = current_price


                    self.trade_history.append({
                    'date': date,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'cost': total_cost,
                    'signal': signal,
                    'cash_after': self.cash
                })

         
                
            if signal < -self.threshold and self.position == 1:
                proceeds_before_fees = self.shares * current_price
                transaction_fee = proceeds_before_fees * self.transaction_cost
                net_proceeds = proceeds_before_fees - transaction_fee

                orginal_cost = self.shares  * self.entry_price
                profit = net_proceeds - orginal_cost
                profit_pct = (current_price -  self.entry_price) / self.entry_price * 100

                self.cash += net_proceeds
                shares_sold = self.shares
                
                self.shares = 0
                self.position = 0
                self.entry_price = None
                
                self.trade_history.append({
                    'date': date,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares_sold,
                    'proceeds': net_proceeds,
                    'signal': signal,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'cash_after': self.cash
                })
        

        if self.position == 1:
            final_date = self.data.index[-1]
            final_price = self.data.loc[final_date, 'Close']
            

            proceeds_before_fees = self.shares * current_price
            transaction_fee = proceeds_before_fees * self.transaction_cost
            net_proceeds = proceeds_before_fees - transaction_fee

            orginal_cost = self.shares  * self.entry_price
            profit = net_proceeds - orginal_cost
            profit_pct = (current_price -  self.entry_price) / self.entry_price * 100

            self.cash += net_proceeds
            shares_sold = self.shares
            
            self.shares = 0
            self.position = 0
            self.entry_price = None
            

            self.trade_history.append({
                    'date': date,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares_sold,
                    'proceeds': net_proceeds,
                    'signal': signal,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'cash_after': self.cash
                })
        
        

        return self.data


    def calculate_metrics(self):

        final_equity = self.cash
        pct_return = (final_equity - self.initial_balance) / self.initial_balance * 100
        number_trades = len(self.trade_history)
        profit_trades = 0
        unprofit_trades = 0
        number_sells = 0
        totalpct = 0
        for trade in self.trade_history:
            if trade['action'] == "SELL":
                if trade['profit'] > 0:
                    profit_trades += 1
                elif trade['profit'] <= 0:
                    unprofit_trades += 1
                totalpct += trade['profit']
                number_sells += 1
        
        avg_return = totalpct / number_sells
        win_rate = profit_trades / number_trades

        max_drawdown = self.calc_max_drawdown()

        return {
        'final_equity' : final_equity,
        'pct_return' : pct_return,
        'number_trades' : number_trades,
        'profit_trades' : profit_trades, 
        'unprofit_trades' : unprofit_trades, 
        'avg_return' : avg_return, 
        'win_rate' : win_rate, 
        'max_drawdown' : max_drawdown
        }

    def calc_max_drawdown(self):
        if len(self.equity_curve) == 0:
            return 0

        peak = self.initial_balance
        max_drawdown = 0 

        for point in self.equity_curve:
            equity = point['equity']

            if equity > peak:
                peak = equity 

            drawdown = (peak - equity) / peak * 100

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown 

    def print_results(self): 

        print("=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)

        metrics = self.calculate_metrics()

        print("PERFORMANCE: ")
        print(f"   Initial Balance: ${self.initial_balance:,.2f}")
        print(f"   Final Balance: ${metrics['final_equity']:,.2f}")
        print(f"   Total Return: {metrics['pct_return']:.2f}%")
        print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")

        print("TRADING ACTIVITY: ")
        print(f"   Total Trades: {metrics['number_trades']}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Avg Trade Return: {metrics['avg_return']:.2f}%")

        print("RECENT TRADES: ")
        for trade in self.trade_history[-5:]:  # Last 5 trades
            action = trade['action']
            date = trade['date']
            price = trade['price']
            shares = trade['shares']
            profit = trade.get('profit', 0)

            if 'SELL' in action:
                print(f"   {date.date()} | {action:12} | ${price:7.2f} × {shares:3} shares | Profit: ${profit:8.2f}")
            else:
                print(f"   {date.date()} | {action:12} | ${price:7.2f} × {shares:3} shares")
    
        print("=" * 70)




    
            







        