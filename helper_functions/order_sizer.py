import backtrader as bt
import math

class OrderSizer(bt.Sizer):
	params = (('stake', 100),)

	def _getsizing(self, comminfo, cash, data, isbuy):
		if isbuy:
			s = math.floor(cash / (self.p.stake * data[0]))
			return s * self.p.stake

		position  = self.broker.getposition(data)
		if not position.size:
			return 0

		return self.p.stake