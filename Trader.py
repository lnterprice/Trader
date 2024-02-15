import json
import webbrowser
from rauth import OAuth1Service
import pdb
from SymbolObj import Symbol
import pandas as pd
import time as tm
import os
import datetime
def symbolQuotes(symbols):
	quotes = {'quotes': {}, 'day': {}}
	time = ""
	for symbol in symbols:
		quote = Symbol(session, symbol)
		if(quote.isOnline()):
			quotes['quotes'][symbol] = {'date': quote.tlastTrade(), 'price': quote.getQuote()}
			time = pd.to_datetime(quotes['quotes'][symbol]['date'], unit='s').date()
		else:
			return -1
			break
	quotes['day'] = str(time)
	return quotes

def createOAuth():
	global session
	global etrade
	CONSUMER_KEY = os.environ['CONSUMER_KEY']
	CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
	etrade = OAuth1Service(
		name="etrade",
		consumer_key=CONSUMER_KEY,
	    consumer_secret=CONSUMER_SECRET,
	    request_token_url="https://api.etrade.com/oauth/request_token",
	    access_token_url="https://api.etrade.com/oauth/access_token",
	    authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
	    base_url="https://api.etrade.com")
	# Requests token to confirm application usage by the user
	request_token, request_token_secret = etrade.get_request_token(params={"oauth_callback": "oob", "format": "json"})
	# Url creation for user confirmation
	authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
	webbrowser.open(authorize_url)
	code = input("Code: ")
	# Requests token verifier, in this case, code
	session = etrade.get_auth_session(request_token, request_token_secret, params={"oauth_verifier": code})

if __name__ == "__main__":
	createOAuth()
	symbols = input("Enter symbols: ")
	symbols = symbols.upper()
	symbols = symbols.split(" ")
	quotes = symbolQuotes(symbols)
	try:
		fileBasePath = os.path.join('D:\\Data Sheets', quotes['day'])
	except TypeError:
		print("Stock market isn't open!")
		exit()
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
			df = pd.read_csv(currentFile)
			df = pd.concat([df, tempDict], ignore_index=True)
			df.to_csv(currentFile, index=False)
		tm.sleep(30)
		quotes = symbolQuotes(symbols)
	print("Stock market has closed!")
	session.get(etrade.base_url + "/oauth/revoke_access_token")
