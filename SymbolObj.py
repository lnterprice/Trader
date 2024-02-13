import json
import pdb
class Symbol:
	def __init__(self, sessionObj, symbol):
		self.sessionObj = sessionObj
		self.symbol = symbol
		self.sessionSymbol = json.loads(self.sessionObj.get('https://api.etrade.com/v1/market/quote/' + self.symbol + '.json').text)['QuoteResponse']['QuoteData'][0]

	def updateData(self):
		self.sessionSymbol = json.loads(self.sessionObj.get('https://api.etrade.com/v1/market/quote/' + self.symbol + '.json').text)['QuoteResponse']['QuoteData'][0]

	def getQuote(self):
		return self.sessionSymbol['All']['lastTrade']

	def isOnline(self):
		#return Trues
		return self.sessionSymbol['quoteStatus'] == "INDICATIVE_REALTIME"

	def tlastTrade(self):
		return self.sessionSymbol['All']['timeOfLastTrade']