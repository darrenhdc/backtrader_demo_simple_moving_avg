import datetime as dt
import backtrader as bt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
class SMAStrategy(bt.Strategy) :
    def __init__(self):
        self.dataclose = self.data0.close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.SimpleMovingAverage(self.data0, period=15)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED，Price: %.2f, Cost; %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                    order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT，GROSS %.2f，NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s'% (dt.isoformat(), txt))

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    dataframe = pd.read_csv('./TSLA.csv')
    dataframe['Datetime'] = pd.to_datetime(dataframe['Date'])
    dataframe.set_index('Datetime', inplace=True)
    data_TSLA = bt.feeds.PandasData(dataname=dataframe, fromdate=dt.datetime(2020,1,2), todate=dt.datetime(2020,12,31), timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data_TSLA)

    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name = 'DrawDown' )

    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.0006)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=90)
    result = cerebro.run()

    print('夏普比率:', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('最大回散:', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'])
    cerebro.plot()
    print("hello world")
