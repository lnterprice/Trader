import pandas as pd
import os
import pdb
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from DF import EDF
basePath = "C:\\Users\\Sphi0\\OneDrive\\Documents\\Python Projects\\Stocker\\Trader\\DataSheets"
osDates = os.listdir(basePath)
app = Dash(__name__)

app.layout = html.Div([
	html.H1('Stock price analysis'),
	html.P('Select Date:'),
	dcc.Dropdown(
		id='dates',
		options=osDates,
		value=osDates[-1],
		clearable=False
	),
	dcc.Graph(id="timeChart"),
	dcc.Graph(id="MACD"),
	html.P("Select Stock:"),
	dcc.Dropdown(
		id="plots",
		clearable=False,
	),
	html.P("Select Indicators:"),
	dcc.Checklist(
		id='strats',
		options={
			'EMACROSSOVER 9 20': 'EMA CoS 9/20',
			'EMACROSSOVER 5 10': 'EMA CoS 5/10',
			'EMACROSSOVER 50 200': 'EMA CoS 50/200',
			'EMACROSSOVER 20 50': 'EMA CoS 20/50',
			'BOLLINGERBANDS 20': 'BB20'
		},
	)
])

def EMACROSSOVER(fig, df, inputs):
	low = inputs[0]
	high = inputs[1]
	df['EMA' + low] = df['price'].ewm(span=int(low), adjust=False).mean()
	df['EMA' + high] = df['price'].ewm(span=int(high), adjust=False).mean()
	#pdb.set_trace()
	#addCrossover(fig, df, 'EMA' + low, 'EMA' + high)
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df['EMA' + low], name='EMA' + low))
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df['EMA' + high], name='EMA' + high))

def BOLLINGERBANDS(fig, df, inputs):
	inputs = int(inputs[0])
	std = df['price'].rolling(window=inputs).std()
	middleBand = df['price'].rolling(window=inputs).mean()
	topBand = middleBand + (std * 2)
	bottomBand = middleBand - (std * 2)
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=middleBand, name='BB Middle'))
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=topBand, name='BB Top'))
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=bottomBand, name='BB Bottom'))

def MACD(fig, df, inputs):
	fast = inputs[0]
	slow = inputs[1]
	ema = inputs[2]
	df[f'MACD {fast}-{slow}'] = df['price'].ewm(span=int(fast), adjust=False).mean() - df['price'].ewm(span=int(slow), adjust=False).mean()
	df[f'SIGNAL {ema}'] = df[f'MACD {fast}-{slow}'].ewm(span=int(ema), adjust=False).mean()
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df[f'MACD {fast}-{slow}'], name='MACD'))
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df[f'SIGNAL {ema}'], name='Signal'))

def epochToPacific(seconds):
	if(type(seconds) != pd.core.series.Series):
		time = pd.to_datetime(seconds, unit='s')
		time = time.tz_localize("UTC")
		time = time.tz_convert('America/Los_Angeles')
		time = time.time()
		time = time.strftime('%I:%M:%S %p')
	else:
		time = pd.to_datetime(seconds, unit='s')
		time = (time).dt.tz_localize("UTC")
		time = (time).dt.tz_convert('America/Los_Angeles')
		time = (time).dt.time

		time = [t.strftime('%I:%M:%S %p') for t in time]
	return time

'''
	df = df.sort_values('date')
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df['buy'], mode='markers', name='Buy Indicator', marker=dict(
		size=16,
		color='green',
		symbol='triangle-down'
	)))
	fig.add_trace(go.Scatter(x=epochToPacific(df['date']), y=df['sell'], mode='markers', name='Sell Indicator', marker=dict(
		size=16,
		color='red',
		symbol='triangle-up'
	)))
	del df['buy']
	del df['sell']


'''


@app.callback(Output('plots', 'options'), Output('plots', 'value'), Input('dates', 'value'))
def getSyms(date):
	listStocks = os.listdir(os.path.join(basePath, date))
	for i, element in enumerate(listStocks):
		listStocks[i] = element[:-4]
	return listStocks, listStocks[0]


@app.callback(Output('timeChart', 'figure'), Output('MACD', 'figure'), Input('dates', 'value'), Input('plots', 'value'), Input('strats', 'value'), Input('timeChart', 'relayoutData'))
def update_graph(date, ticker, strats, zoomLevel):
	df = pd.read_csv(os.path.join(basePath, date, ticker + ".csv"))
	dfEpoch = pd.read_csv(os.path.join(basePath, date, ticker + ".csv"))
	fig = go.Figure()
	macd = go.Figure()
	df['date'] = df['date'].astype('float')
	dfEpoch['date'] = dfEpoch['date'].astype('float')
	#pdb.set_trace()
	df['12-Period EMA'] = df['price'].ewm(span=12).mean()
	df['26-Period EMA'] = df['price'].ewm(span=26).mean()
	df['MACD'] = df['12-Period EMA'] - df['26-Period EMA']
	df['Signal Line'] = df['MACD'].ewm(span=9).mean()
	df.date = epochToPacific(df.date)
	fig.add_trace(go.Scatter(x=df['date'], y=df['price'], name=ticker))
	macd.add_trace(go.Scatter(x=df['date'], y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
	macd.add_trace(go.Scatter(x=df['date'], y=df['Signal Line'], mode='lines', name='Signal Line', line=dict(color='orange')))
	macd.add_trace(go.Bar(x=df['date'], y=df['MACD'] - df['Signal Line'], name='Histogram'))
	try:
		strats = tuple(strats)
		for strat in strats:
			#pdb.set_trace()
			strat = strat.split(" ")
			indicator, inputs = strat[0], strat[1:]
			exec(f"{indicator}(fig, dfEpoch, inputs)")
			#pdb.set_trace()
	except TypeError:
		pass
	
	try:
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=700, 
			xaxis_range=[zoomLevel['xaxis.range[0]'], zoomLevel['xaxis.range[1]']],
			yaxis_range=[zoomLevel['yaxis.range[0]'], zoomLevel['yaxis.range[1]']]
		)
	except TypeError:
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=700)
	except KeyError:
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=700, 
			xaxis_autorange=True,
			yaxis_autorange=True
		)
	macd.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='MACD'))
	return fig, macd

app.run_server(debug=True)