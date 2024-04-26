import pandas as pd
import os
import pdb
import plotly.graph_objects as go
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
			'EMACROSSOVER 5 10': 'EMA CoS 5/10',
			'EMACROSSOVER 9 20': 'EMA CoS 9/20',
			'EMACROSSOVER 50 200': 'EMA CoS 50/200',
			'EMACROSSOVER 20 50': 'EMA CoS 20/50',
			'BOLLINGERBANDS 20': 'BB20'
		},
	),
	html.Button('Enable/Disable Strategies', id='toggle'),
	html.Button('Enable/Disable MACD Indicators', id='macdT')
])

def graphIndicators(fig, df):
	fig.add_trace(go.Scatter(x=df.getRows('time'), y=df.getRows('buy'), mode='markers', name='Sell Indicator', marker=dict(
		color='green',
		size=16,
		symbol='triangle-down'
	)))
	fig.add_trace(go.Scatter(x=df.getRows('time'), y=df.getRows('sell'), mode='markers', name='Buy Indicator', marker=dict(
		color='red',
		size=16,
		symbol='triangle-up'
	)))

def EMACROSSOVER(fig, df, inputs, enabled):
	low = inputs[0]
	high = inputs[1]
	df.setColumn(
		'EMA' + low,
		df.getRows('price').ewm(span=int(low), adjust=False).mean()
	)
	df.setColumn(
		'EMA' + high,
		df.getRows('price').ewm(span=int(high), adjust=False).mean()
	)
	df.insertIndicators('EMA' + low, 'EMA' + high)
	if enabled:
		lines['EMA' + low] = fig
		lines['EMA' + high] = fig

def BOLLINGERBANDS(fig, df, inputs, enabled):
	inputs = int(inputs[0])
	std = df.getRows('price').rolling(window=inputs).std()
	middleBand = df.getRows('price').rolling(window=inputs).mean()
	topBand = middleBand + (std * 2)
	bottomBand = middleBand - (std * 2)
	df.setColumn(
		'middleBand',
		middleBand
	)
	df.setColumn(
		'topBand',
		topBand
	)
	df.setColumn(
		'bottomBand',
		bottomBand
	)
	if enabled:
		lines['middleBand'] = fig
		lines['topBand'] = fig
		lines['bottomBand'] = fig

def MACD(fig, df, inputs, enabled):
	fast = inputs[0]
	slow = inputs[1]
	ema = inputs[2]
	df.setColumn(
		f'MACD {fast}-{slow}', 
		df.getRows('price').ewm(span=int(fast), adjust=False).mean() - df.getRows('price').ewm(span=int(slow), adjust=False).mean()
	)
	df.setColumn(
		f'SIGNAL {ema}',
		df.getRows(f'MACD {fast}-{slow}').ewm(span=int(ema), adjust=False).mean()
	)
	if enabled:
		df.insertIndicators(f'MACD {fast}-{slow}', f'SIGNAL {ema}')
	lines[f'MACD {fast}-{slow}'] = fig
	lines[f'SIGNAL {ema}'] = fig



def addLines(df):
	for key, value in lines.items():
		value.add_trace(go.Scatter(x=df.getRows('time'), y=df.getRows(key), name=key))

@app.callback(Output('plots', 'options'), Output('plots', 'value'), Input('dates', 'value'))
def getSyms(date):
	listStocks = os.listdir(os.path.join(basePath, date))
	for i, element in enumerate(listStocks):
		listStocks[i] = element[:-4]
	return listStocks, listStocks[0]


@app.callback(Output('timeChart', 'figure'), Output('MACD', 'figure'), Input('dates', 'value'), Input('plots', 'value'), Input('strats', 'value'), Input('timeChart', 'relayoutData'), Input('toggle', 'n_clicks'), Input('macdT', 'n_clicks')	)
def update_graph(date, ticker, strats, zoomLevel, graph, macdt):
	global lines
	df = EDF(pd.read_csv(os.path.join(basePath, date, ticker + ".csv")))
	lines = {}
	fig = go.Figure()
	macd = go.Figure()
	df.renameCol('date', 'epoch')
	df.updateTime()
	enabled = graph == None or graph % 2 == 0
	enabledMac = macdt == None or macdt % 2 == 0
	MACD(macd, df, [12, 16, 9], enabledMac)
	try:
		strats = tuple(strats)
		for strat in strats:
			strat = strat.split(" ")
			indicator, inputs = strat[0], strat[1:]
			exec(f"{indicator}(fig, df, inputs, enabled)")
	except TypeError:
		pass
	addLines(df)
	graphIndicators(fig, df)
	fig.add_trace(go.Scatter(x=df.getRows('time'), y=df.getRows('price'), name=ticker, line=dict(color='grey')))
	macd.add_trace(go.Bar(x=df.getRows('time'), y=df.getRows('MACD 12-16') - df.getRows('SIGNAL 9'), name='Histogram'))

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