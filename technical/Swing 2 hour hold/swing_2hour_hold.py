from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
from backtrader.indicators import EMA

# Import custom classes
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/helper_functions')
sys.path.append('/Users/m4punk/Documents/Coding/python/QuantTrading/Quant-Strategies/datas/Scripts')
import order_sizer, get_universe

