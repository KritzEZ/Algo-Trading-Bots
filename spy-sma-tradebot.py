#Trading bot go long if SPY is in uptrend (above 30-day SMA) and within 5% of 52-week high
#go short if SPY is in downtrend (below 30-day SMA) and within 5% of 52-week low
#liquidate if it fall out of these ranges

#Plotting SMA, 52-week high and 52-week low

# region imports
from AlgorithmImports import *
from collections import deque
# endregion

class AdaptableApricotJellyfish(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2021, 1, 1)
        self.set_cash(100000)
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol

        #  self.sma = self.sma(self.spy, 30, Resolution.DAILY)
        #  closing_prices = self.history(self.spy, 30, Resolution.DAILY)["close"]
        #  for time, price in closing_prices.loc[self.spy].items():
        #     self.sma.Update(time, price)
        self.sma = CustomSimpleMovingAverage("CustomSMA", 30)
        self.register_indicator(self.spy, self.sma, Resolution.DAILY)


    def on_data(self, data: Slice):
        if not self.sma.IsReady:
            return

        hist = self.history(self.spy, timedelta(365), Resolution.DAILY)
        low = min(hist["low"])
        high = max(hist["high"])

        price = self.securities[self.spy].price

        if price * 1.05 >= high and self.sma.current.value < price:
            if not self.portfolio[self.spy].IsLong:
                self.set_holdings(self.spy, 1)
        
        elif price * 0.95 <= low and self.sma.current.value > price:
            if not self.portfolio[self.spy].IsShort:
                self.set_holdings(self.spy, -1)

        else:
            self.liquidate()

        self.Plot("Benchmark", "52w-High", high)
        self.Plot("Benchmark", "52w-Low", low)
        self.Plot("Benchmark", "SMA", self.sma.current.value)


class CustomSimpleMovingAverage(PythonIndicator):

    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)

    def Update(self, input):
        self.queue.append(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue)/count
        return (count == self.queue.maxlen)