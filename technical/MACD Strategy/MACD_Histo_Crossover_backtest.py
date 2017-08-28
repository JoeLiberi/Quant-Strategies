from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
from backtrader.indicators import EMA
import backtrader.analyzers as btanalyzers
from indicators.MACD import MACD
from helper_functions import order_sizer

# Create a Stratey
class macd_crossover(bt.Strategy):

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

		self.macd = MACD(self.datas[0])
        
	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f' %
					(order.executed.price,
					order.executed.value,
					order.executed.comm,
					order.executed.size))

				self.buyprice = order.executed.price
				self.buycomm = order.executed.comm
			elif order.issell(): # Sell
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f Size: %.2f' % 
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm,
					 order.executed.size))
				
			self.bar_executed = len(self)


		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected/Expired')

		self.order = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
				(trade.pnl, trade.pnlcomm))

	def next(self):

		timestamp = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()


		# Simply log the closing price of the series from the reference
		self.log('Close, %.2f' % self.dataclose[0])

		if self.order:
			# if timestamp > self.order.valid:
			if self.order.Expired:
				self.broker.cancel(self.order)
				self.order = None
			return

		if -0.5 < self.macd.l.histo[0] < 0.5:
			return

		# Check if we are in the market
		if not self.position:

			# if self.macd.l.macd[2] > 0:

			if self.macd.l.macd[0] > self.macd.l.signal[0]:

				# BUY, BUY, BUY!!!! (with all possible default parameters)
				self.log('BUY CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				# self.order = self.buy()

				# Limit Order
				self.order = self.buy( exectype= bt.Order.Limit,
										price = self.dataclose[0] * 0.98,
										valid = timestamp)

			# elif self.macd.l.macd[2] < 0:
			if self.macd.l.macd[0] < self.macd.l.signal[0]:
				# SELL, SELL, SELL!!! (with all possible default parameters)
				self.log('SHORT CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.sell(exectype= bt.Order.Limit,
											price = self.dataclose[0] * 1.01,
											valid = timestamp)
		else:
			if self.position.size > 0:
				if self.macd.l.macd[0] < self.macd.l.signal[0]:
					self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
					self.order = self.close()

			elif self.position.size < 0:
				if self.macd.l.macd[0] > self.macd.l.signal[0]: 
					self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
					self.order = self.close()

	def stop(self):
		print('==================================================')
		print('Starting Value - %.2f' % self.broker.startingcash)
		print('Ending   Value - %.2f' % self.broker.getvalue())
		print('==================================================')

if __name__ == '__main__':

	cash = 25000.0
	# Init Cerebro
	cerebro = bt.Cerebro()

	# Add a strategy
	cerebro.addstrategy(macd_crossover)


    # Create a Data Feed
	dataframe = pd.read_csv('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/twtr.csv',
			parse_dates=True,
			index_col=0,
			na_values=['-']
		)

	dataframe = dataframe.iloc[::-1]

	data = btfeeds.PandasData(
		timeframe=bt.TimeFrame.Days, compression=1,
		dataname=dataframe,
		open=0,
		high=1,
		low=2,
		close=3,
		volume=4,
		openinterest=None
	)

	# Add the Data Feed to Cerebro
	cerebro.adddata(data)

	# Set Cash
	cerebro.broker.setcash(cash)

	# Set seizer
	cerebro.addsizer(order_sizer.OrderSizer)

    # Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)

	# Analyzer
	cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	thestrats = cerebro.run()
	thestrat = thestrats[0]
	print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis()['sharperatio'])


	cerebro.plot()