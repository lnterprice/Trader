import webbrowser
from rauth import OAuth1Service
import pdb
from SymbolObj import Symbol
import pandas as pd
import time as tm
import os
import datetime

class DataPoints:

	def __init__(self):
		self.dsPath = os.environ['DATA_SHEETS']
		self.createOAuth()

	def symbolQuotes(self, symbols, test=False):
		quotes = {'quotes': {}, 'day': {}}
		time = ""
		for symbol in symbols:
			quote = Symbol(self.session, symbol)
			if(quote.isOnline() or test):
				success = False
				while not success:
					try:
						quotes['quotes'][symbol] = {'date': quote.tlastTrade(), 'price': quote.getQuote()}
						time = pd.to_datetime(quotes['quotes'][symbol]['date'], unit='s').date()
						success = True
					except KeyError:
						pass
			else:
				return -1
		quotes['day'] = str(time)
		return quotes

	def createOAuth(self):
		CONSUMER_KEY = os.environ['CONSUMER_KEY']
		CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
		self.etrade = OAuth1Service(
			name="etrade",
			consumer_key=CONSUMER_KEY,
			consumer_secret=CONSUMER_SECRET,
			request_token_url="https://api.etrade.com/oauth/request_token",
			access_token_url="https://api.etrade.com/oauth/access_token",
			authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
			base_url="https://api.etrade.com")
		# Requests token to confirm application usage by the user
		request_token, request_token_secret = self.etrade.get_request_token(params={"oauth_callback": "oob", "format": "json"})
		# Url creation for user confirmation
		authorize_url = self.etrade.authorize_url.format(self.etrade.consumer_key, request_token)
		webbrowser.open(authorize_url)
		code = input("Code: ")
		# Requests token verifier, in this case, code
		self.session = self.etrade.get_auth_session(request_token, request_token_secret, params={"oauth_verifier": code})

	def stall(self):
		now = datetime.datetime.now()
		time = datetime.datetime(now.year, now.month, now.day, 6, 30)
		if now > time:
			time = time + datetime.timedelta(days=1)
		timeDif = time - now
		totalSeconds = timeDif.seconds
		while totalSeconds != 0:
			if totalSeconds < 5400:
				tm.sleep(totalSeconds)
				totalSeconds = 0
			else:
				tm.sleep(5400)
				self.session.get('https://api.etrade.com/v1/market/quote/AAPL.json').text
				totalSeconds -= 5400

	def run(self, test=False):
		symbols = input("Enter symbols: ")
		symbols = symbols.upper()
		symbols = symbols.split(" ")
		quotes = self.symbolQuotes(symbols, test)
		if quotes == -1:
			self.stall()
		quotes = self.symbolQuotes(symbols, test)
		fileBasePath = os.path.join(self.dsPath, quotes['day'])
		try:
			os.mkdir(fileBasePath)
		except FileExistsError:
			pass
		
		for quote in quotes['quotes']:
			try:
				f = open(os.path.join(fileBasePath, quote + ".csv"), "x")
				f.close()
				df = pd.DataFrame(columns=['date', 'price', 'color', 'custom_data'])
				df.to_csv(os.path.join(fileBasePath, quote + ".csv"), index=False)
			except FileExistsError or PermissionError:
				pass
		while quotes != -1:
			for i, quote in enumerate(quotes['quotes']):
				currentFile = os.path.join(fileBasePath, quote + ".csv")
				time = quotes['quotes'][quote]['date']
				quotePrice = quotes['quotes'][quote]['price']
				tempDict = pd.DataFrame([{

					'date': time,
					'price': float(quotePrice),
					'color': quote,
					'custom_data': quote

					}])
				success = False
				while not success:
					try:
						df = pd.read_csv(currentFile)
						df = pd.concat([df, tempDict], ignore_index=True)
						df.to_csv(currentFile, index=False)
						success = True
					except PermissionError:
						pass
			tm.sleep(30)
			quotes = self.symbolQuotes(symbols)
		print("Stock market has closed!")
		self.session.get(self.etrade.base_url + "/oauth/revoke_access_token")

	def concatDFS(self, symbolObj):
		#pdb.set_trace()
		DF = pd.DataFrame()
		for dir in os.listdir(self.dsPath):
			symbolDir = os.path.join(self.dsPath, dir, symbolObj.returnSymbol() + '.csv')
			if os.path.exists(symbolDir):
				DF = pd.concat([DF, pd.read_csv(symbolDir)], ignore_index=True)
		
		return DF
	
	def getSession(self):
		return self.session