import json
import pdb
import datetime
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
        return datetime.datetime.now().time() < datetime.time(13, 0) and datetime.datetime.now().time() >= datetime.time(6, 30)

    def tlastTrade(self):
        return self.sessionSymbol['All']['timeOfLastTrade']
    
    def returnSymbol(self):
        return self.symbol