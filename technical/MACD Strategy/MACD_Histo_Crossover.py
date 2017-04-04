from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
from backtrader.indicators import EMA
import math

# Import custom classes
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/helper_functions')
import order_sizer

class MACD(bt.Indicator):
	lines = ('macd', 'signal', 'histo',)
	params = (('period_me1', 12), ('period_me2', 26), ('period_signal', 9),)

	def __init__(self):
		me1 = EMA(self.data, period=self.p.period_me1)
		me2 = EMA(self.data, period=self.p.period_me2)
		self.l.macd = me1 - me2
		self.l.signal = EMA(self.l.macd, period=self.p.period_signal)
		self.l.histo = self.l.macd - self.l.signal

# Create a Stratey
class macd_crossover(bt.Strategy):

	params = (('stake', 100),)

	def __init__(self):
		# Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close

		self.order = None
		
		self.buyprice = None
		self.buycomm = None

		self.macd = MACD(self.datas[0])

	def log(self, txt, dt=None):
		''' Logging function for this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))
        
	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f' %
					(order.executed.price,
					order.executed.value,
					order.executed.comm,
					order.executed.size))

				self.buyprice = order.executed.price
				self.buycomm = order.executed.comm
			else: # Sell
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f Size: %.2f' % 
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm,
					 order.executed.size))

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

			if self.macd.l.macd[0] > self.macd.l.signal[0]:

				# BUY, BUY, BUY!!!! (with all possible default parameters)
				self.log('BUY CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				# self.order = self.buy()

				# Limit Order
				order_size = math.floor(self.broker.cash / (self.p.stake * self.dataclose[0])) * self.p.stake

				self.order = self.buy( exectype= bt.Order.Limit,
										price = self.dataclose[0] * 1.02,
										valid = datetime.datetime.now() + datetime.timedelta(days=3),
										size = order_size)

		else:
			if self.macd.l.macd[0] < self.macd.l.signal[0]:
				# SELL, SELL, SELL!!! (with all possible default parameters)
				self.log('SELL CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.sell(size=self.p.stake)

	def stop(self):
		print('==================================================')
		print('Starting Value - %.2f' % self.broker.startingcash)
		print('Ending   Value - %.2f' % self.broker.getvalue())
		print('==================================================')