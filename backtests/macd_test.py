from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
from yahoo_finance import Share
from pprint import pprint

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

# Import custom classes
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/technical/MACD Strategy')
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/helper_functions')
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/Scripts')
import order_sizer
from MACD_Histo_Crossover import macd_crossover
import universe

if __name__ == '__main__':

	fromdate=datetime.datetime(2014, 1, 1)
	todate=datetime.datetime(2014, 12, 31)

	universe = universe.GetUniverse(fromdate, todate)
	stocks = universe.get_stocks()
	stocks = stocks[:5]
	data_dict = {}

	cash = 10000.0

	# Init Cerebro
	cerebro = bt.Cerebro()

	# Add a strategy
	cerebro.addstrategy(macd_crossover)

	# for stock in stocks[:2]:
	data0 = universe.get_data(stocks[0])
	cerebro.adddata(data0)

	data1 = universe.get_data(stocks[1])
	cerebro.adddata(data1)

	# Set Cash
	cerebro.broker.setcash(cash)

	# Set seizer
	cerebro.addsizer(order_sizer.OrderSizer)

    # Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)

	# print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	# print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.plot(style='bar')