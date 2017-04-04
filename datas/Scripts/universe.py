import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import csv
from yahoo_finance import Share
import pandas as pd
import backtrader.feeds as btfeeds

'''

	get_universe.py 

	Parse through the Nasdaq and NYSE csv files, print out all stocks in a specific price range.

'''

class GetUniverse():

	def __init__(self, fromdate, todate, nasdaq_file=None, nyse_file=None, max_price=3.0, min_price=0.50):

		if nasdaq_file is None:
			self.nasdaq_file = "/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/NASDAQ_Company_List.csv"
		else:
			self.nasdaq_file = nasdaq_file

		if nyse_file is None:
			self.nyse_file = "/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/NYSE_Company_List.csv"
		else:
			self.nyse_file = nyse_file

		self.file_list = [self.nasdaq_file, self.nyse_file]
		self.symbol_list = []
		self.max_price = max_price
		self.min_price = min_price
		self.fromdate = fromdate
		self.todate = todate


	def get_stocks(self):
		for f in self.file_list:
			with open(f, newline='') as csvfile:
				reader = csv.DictReader(csvfile)
				for row in reader:
					if row['LastSale'] == 'n/a':
						continue

					lastsale = float(row['LastSale'])
					if lastsale < self.max_price and lastsale > self.min_price:
						# print(row['Symbol'])
						self.symbol_list.append(row['Symbol'])

		return(self.symbol_list)

	def get_data(self, stock):


			# single_data = yahoo.get_historical(self.fromdate, self.todate)
			# df = pd.DataFrame(single_data)
			# df = df.set_index('Date')
			# return(df)
		    # Create a Data Feed
		data = btfeeds.YahooFinanceData(
			dataname=stock,
			fromdate=self.fromdate,
			todate=self.todate)

		return data
			

