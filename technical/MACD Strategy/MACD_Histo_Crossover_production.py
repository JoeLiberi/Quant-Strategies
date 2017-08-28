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

		self.counttostop = 0
		self.datastatus = False

		self.macd = MACD(self.datas[0])

		print('--------------------------------------------------')
		print('Strategy Created')
		print('--------------------------------------------------')
        

	def notify_data(self, data, status, *args, **kwargs):
		# print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)

		if status == data.LIVE:
			print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
			self.datastatus = True

	def notify_store(self, msg, *args, **kwargs):
		print('*' * 5, 'STORE NOTIF:', msg)

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

		print('-' * 50, 'ORDER BEGIN', datetime.datetime.now())
		print(order)
		print('-' * 50, 'ORDER END')

		self.order = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		print('-' * 50, 'TRADE BEGIN', datetime.datetime.now())
		print(trade)
		print('-' * 50, 'TRADE END')

	def next(self):

		txt = list()
		txt.append('%04d' % len(self))
		dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
		txt.append('%s' % self.data.datetime.datetime(0).strftime(dtfmt))
		txt.append('{}'.format(self.data.open[0]))
		txt.append('{}'.format(self.data.high[0]))
		txt.append('{}'.format(self.data.low[0]))
		txt.append('{}'.format(self.data.close[0]))
		txt.append('{}'.format(self.data.volume[0]))
		txt.append('{}'.format(self.data.openinterest[0]))
		txt.append('{}'.format(self.macd.l.macd[0]))
		txt.append('{}'.format(self.macd.l.signal[0]))
		print(', '.join(txt))

		if len(self.datas) > 1:
			txt = list()
			txt.append('%04d' % len(self))
			dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
			txt.append('%s' % self.data1.datetime.datetime(0).strftime(dtfmt))
			txt.append('{}'.format(self.data1.open[0]))
			txt.append('{}'.format(self.data1.high[0]))
			txt.append('{}'.format(self.data1.low[0]))
			txt.append('{}'.format(self.data1.close[0]))
			txt.append('{}'.format(self.data1.volume[0]))
			txt.append('{}'.format(self.data1.openinterest[0]))
			txt.append('{}'.format(float('NaN')))
			print(', '.join(txt))

		if self.counttostop:  # stop after x live lines
			self.counttostop -= 1
			if not self.counttostop:
				self.env.runstop()
				return


		timestamp = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()

		if self.order:
			# if timestamp > self.order.valid:
			if self.order.Expired:
				self.broker.cancel(self.order)
				self.order = None
			return

		# if -0.5 < self.macd.l.histo[0] < 0.5:
		# 	return

		# Check if we are in the market
		if self.datastatus and not self.position:

			print('BUY CREATE, %.2f' % self.dataclose[0])

			# Limit Order
			self.order = self.buy( exectype = bt.Order.Limit,
									price = self.dataclose[0])

			# if self.macd.l.macd[2] > 0:

		# 	if self.macd.l.macd[0] > self.macd.l.signal[0]:

		# 		# BUY, BUY, BUY!!!! (with all possible default parameters)
		# 		self.log('BUY CREATE, %.2f' % self.dataclose[0])

		# 		# Keep track of the created order to avoid a 2nd order
		# 		# self.order = self.buy()

		# 		# Limit Order
		# 		self.order = self.buy( exectype= bt.Order.Limit,
		# 								price = self.dataclose[0] * 0.98,
		# 								valid = timestamp)

		# 	# elif self.macd.l.macd[2] < 0:
		# 	if self.macd.l.macd[0] < self.macd.l.signal[0]:
		# 		# SELL, SELL, SELL!!! (with all possible default parameters)
		# 		self.log('SHORT CREATE, %.2f' % self.dataclose[0])

		# 		# Keep track of the created order to avoid a 2nd order
		# 		self.order = self.sell(exectype= bt.Order.Limit,
		# 									price = self.dataclose[0] * 1.01,
		# 									valid = timestamp)
		# else:
		# 	if self.position.size > 0:
		# 		if self.macd.l.macd[0] < self.macd.l.signal[0]:
		# 			self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
		# 			self.order = self.close()

		# 	elif self.position.size < 0:
		# 		if self.macd.l.macd[0] > self.macd.l.signal[0]: 
		# 			self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
		# 			self.order = self.close()

	def stop(self):
		print('==================================================')
		print('Starting Value - %.2f' % self.broker.startingcash)
		print('Ending   Value - %.2f' % self.broker.getvalue())
		print('==================================================')

	def start(self):
		if self.data0.contractdetails is not None:
			print('Timezone from ContractDetails: {}'.format(self.data0.contractdetails.m_timeZoneId))

		header = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume','OpenInterest', 'MACD', 'Signal']
		print(', '.join(header))

		self.done = False

if __name__ == '__main__':

	# Init Cerebro
	cerebro = bt.Cerebro()

	# Add a strategy
	cerebro.addstrategy(macd_crossover)

	# Connect to trading platform
	ibstore = bt.stores.IBStore(host='127.0.0.1', port=7496)

	# Get broker information
	cerebro.broker = ibstore.getbroker()

	data = ibstore.getdata(
		dataname='TWTR-STK-SMART',
		timeframe=bt.TimeFrame.Minutes, 
		compression=5
		)

	# Add the Data Feed to Cerebro
	cerebro.adddata(data)

	# Set Cash for backtrading
	# cerebro.broker.setcash(cash)

	# Set seizer
	cerebro.addsizer(order_sizer.OrderSizer)

	# Analyzer
	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.run(exactbars=True)


	cerebro.plot()