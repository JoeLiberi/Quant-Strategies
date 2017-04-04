from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

# Create a Stratey
class TestStrategy(bt.Strategy):

	params = (
		('maperiod', 15),
	)

	def log(self, txt, dt=None):
		''' Logging function for this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		# Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close

		self.order = None
		
		self.buyprice = None
		self.buycomm = None

		self.sma = bt.indicators.SimpleMovingAverage(
			self.datas[0], period=self.params.maperiod)

		# Indicators for the plotting show
		bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
		bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
											subplot=True)
		bt.indicators.StochasticSlow(self.datas[0])
		bt.indicators.MACDHisto(self.datas[0])
		rsi = bt.indicators.RSI(self.datas[0])
		bt.indicators.SmoothedMovingAverage(rsi, period=10)
		bt.indicators.ATR(self.datas[0], plot=False)
        
	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
					(order.executed.price,
					order.executed.value,
					order.executed.comm))

				self.buyprice = order.executed.price
				self.buycomm = order.executed.comm
			else: # Sell
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % 
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm))

			self.bar_executed = len(self)

		self.order = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
				(trade.pnl, trade.pnlcomm))

	def next(self):
		# Simply log the closing price of the series from the reference
		self.log('Close, %.2f' % self.dataclose[0])

		if self.order:
			return

		# Check if we are in the market
		if not self.position:

			if self.dataclose[0] < self.sma[0]:

				# BUY, BUY, BUY!!!! (with all possible default parameters)
				self.log('BUY CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.buy()

		else:
			if self.dataclose[0] > self.sma[0]:
				# SELL, SELL, SELL!!! (with all possible default parameters)
				self.log('SELL CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.sell()

if __name__ == '__main__':

	# Init Cerebro
	cerebro = bt.Cerebro()

	# Add a strategy
	cerebro.addstrategy(TestStrategy)

	# Datas are in a subfolder of the samples. Need to find where the script is
	# because it could have been called from anywhere
	modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
	datapath = os.path.join(modpath, '../datas/bac_data_5yd_daily.csv')

    # Create a Data Feed
	data = btfeeds.YahooFinanceData(
		dataname='BAC',
		fromdate=datetime.datetime(2013, 1, 3),
		todate=datetime.datetime(2015, 12, 31))

	# Add a FixedSize sizer according to the stake
	cerebro.addsizer(bt.sizers.FixedSize, stake=100)

	# Add the Data Feed to Cerebro
	cerebro.adddata(data)

	# Set Cash
	cerebro.broker.setcash(10000.0)

    # Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.plot()