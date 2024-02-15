import pandas as pd
import os
import pdb
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
basePath = "C:\\Users\\Sphi0\\OneDrive\\Documents\\Python Projects\\Stocker\\DataSheets"
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
			'EMACROSSOVER 50 200': 'EMA CoS 50/200'
		},
		value=['EMACROSSOVER 9 20']
	)
])

def EMACROSSOVER(fig, df, inputs):
	low = inputs[0]
	high = inputs[1]
	df['EMA' + low] = df['price'].ewm(span=int(low), adjust=False).mean()
	df['EMA' + high] = df['price'].ewm(span=int(high), adjust=False).mean()
	fig.add_trace(go.Scatter(x=df['date'], y=df['EMA' + low], name='EMA' + low))
	fig.add_trace(go.Scatter(x=df['date'], y=df['EMA' + high], name='EMA' + high))


@app.callback(Output('plots', 'options'), Output('plots', 'value'), Input('dates', 'value'))
def getSyms(date):
	listStocks = os.listdir(os.path.join(basePath, date))
	for i, element in enumerate(listStocks):
		listStocks[i] = element[:-4]
	return listStocks, listStocks[0]


@app.callback(Output('timeChart', 'figure'), Input('dates', 'value'), Input('plots', 'value'), Input('strats', 'value'), Input('timeChart', 'relayoutData'))
def update_graph(date, ticker, strats, zoomLevel):
	df = pd.read_csv(os.path.join(basePath, date, ticker + ".csv"))
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df['date'], y=df['price'], name=ticker))
	try:
		strats = tuple(strats)
		for strat in strats:
			strat = strat.split(" ")
			indicator, inputs = strat[0], strat[1:]
			exec(f"{indicator}(fig, df, inputs)")
	except TypeError:
		pass
	try:
		print(zoomLevel)
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=1000, 
			xaxis_range=[zoomLevel['xaxis.range[0]'], zoomLevel['xaxis.range[1]']],
			yaxis_range=[zoomLevel['yaxis.range[0]'], zoomLevel['yaxis.range[1]']]
		)
	except TypeError:
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=1000)
	except KeyError:
		fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'), autosize=False, width=1920, height=1000, 
			xaxis_autorange=True,
			yaxis_autorange=True
		)
	return fig

app.run_server(debug=True)
