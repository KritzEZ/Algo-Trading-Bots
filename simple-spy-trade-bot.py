# region imports
from AlgorithmImports import *
# endregion

#Bot buys SPY, sells when price has moved 10% (positive/negative), waits for 31 days after and repeats cycle. 

class MuscularOrangeGalago(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2021, 1, 1)      
        self.set_cash(100000)

        spy = self.add_equity("SPY", Resolution.Daily)
        spy.set_data_normalization_mode(DataNormalizationMode.Raw)

        self.spy = spy.symbol

        self.set_benchmark("SPY")
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time
    

    def on_data(self, data: Slice):
        if not data.contains_key(self.spy):
            self.debug(f"No data for {self.spy} at {self.time}")
            return

        tradeBar = data.bars.get(self.spy)
        if tradeBar is None:
            self.debug(f"No TradeBar data for {self.spy} at {self.time}")
            return

        price = tradeBar.close

        if not self.Portfolio.Invested:
            if self.nextEntryTime <= self.Time:
                self.set_holdings(self.spy, 1)
                #self.market_order(self.spy, int(self.portfolio.Cash / price))
                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price

        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
            self.liquidate()
            self.Log("SELL SPY @" + str(price))
            self.nextEntryTime = self.Time + self.period


