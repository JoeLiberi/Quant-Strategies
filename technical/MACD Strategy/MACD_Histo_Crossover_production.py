import backtrader as bt

ibstore = bt.stores.IBStore(host='127.0.0.1', port=7496, clientId=35)
data = ibstore.getdata(dataname='EUR.USD-CASH-IDEALPRO')



