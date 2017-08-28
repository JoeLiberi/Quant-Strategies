# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
from backtrader.indicators import EMA


class MACD(bt.Indicator):
	lines = ('macd', 'signal', 'histo',)
	params = (('period_me1', 12), ('period_me2', 26), ('period_signal', 9),)

	def __init__(self):
		me1 = EMA(self.data, period=self.p.period_me1)
		me2 = EMA(self.data, period=self.p.period_me2)
		self.l.macd = me1 - me2
		self.l.signal = EMA(self.l.macd, period=self.p.period_signal)
		self.l.histo = self.l.macd - self.l.signal