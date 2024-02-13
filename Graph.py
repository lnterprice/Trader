import pandas as pd
import os
import pdb
import datetime
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
		id='ind',
		options={
			'EMA9': 'EMA9',
			'EMA20': 'EMA20'
		}
	)
])

@app.callback(Output('plots', 'options'), Output('plots', 'value'), Input('dates', 'value'))
def getSyms(date):
	listStocks = os.listdir(os.path.join(basePath, date))
	for i, element in enumerate(listStocks):
		listStocks[i] = element[:-4]
	return listStocks, listStocks[0]


@app.callback(Output('timeChart', 'figure'), Input('dates', 'value'), Input('plots', 'value'), Input('ind', 'value'))
def update_graph(date, ticker, inds):
	df = pd.read_csv(os.path.join(basePath, date, ticker + ".csv"))
	df.date = pd.to_datetime(df.date)
	df.date = (df.date).dt.tz_localize("UTC")
	df.date = (df.date).dt.tz_convert('America/Los_Angeles')
	df.date = (df.date).dt.time
	df.date = [t.strftime('%H:%M:%S %p') for t in df.date]
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df['date'], y=df['price'], name=ticker))
	#fig.add_trace(go.Scatter(x=df['date'], y=df['EMA5'], name=f'{ticker} SMA 5'))
	#fig.add_trace(go.Scatter(x=df['date'], y=df['EMA10'], name=f'{ticker} SMA 10'))
	#fig = px.line(df, x='date', y='price', title = ticker, color='color', custom_data='custom_data')
	try:
		for indicator in inds:
			head = indicator.rstrip("0123456789")
			tail = indicator[len(head):]
			df[head] = df['price'].ewm(span=int(tail), adjust=False).mean()
			fig.add_trace(go.Scatter(x=df['date'], y=df[head], name=indicator))
	except TypeError:
		pass
	fig.update_layout(xaxis=dict(title='Time', tickmode='linear', tick0=-60, dtick=50), yaxis = dict(title='Price'))
	return fig

app.run_server(debug=True)
