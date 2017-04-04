#!/usr/local/bin/python3

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import csv
import requests

'''

	get_stock_list.py 

	Download the Nasaq and NYSE csv files from www.nasdaq.com

	Nasdaq: http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
	NYSE: http://http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download

'''

nasdaq_file = "/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/NASDAQ_Company_List.csv"
nyse_file = "/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/NYSE_Company_List.csv"
nasdaq_url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
nyse_url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"

file_list = [nasdaq_file, nyse_file]
url_list = [nasdaq_url, nyse_url]

if __name__ == '__main__':

	for url, fl in zip(url_list, file_list):
		u = requests.get(url)

		with open(fl, 'wb') as f:
			for chunk in u.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					f.flush()