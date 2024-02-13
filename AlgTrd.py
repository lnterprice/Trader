import os
import pandas as pd
import pdb
import vectorbt as vbt
baseDir = 'C:\\Users\\Sphi0\\OneDrive\\Documents\\Python Projects\\Stocker\\DataSheets\\2024-02-13'
total_profit = 0
for element in os.listdir(baseDir):
	data = pd.read_csv(os.path.join(baseDir, element))
	data.set_index('date', inplace=True)
	data.rename_axis('Date', inplace=True)
	price = data['price']
	fast_ma = vbt.MA.run(price, 9, ewm=True)
	slow_ma = vbt.MA.run(price, 20, ewm=True)
	# Fast crossover = buy
	entries = fast_ma.ma_crossed_above(slow_ma)
	# Slow crossover = sell
	exits = fast_ma.ma_crossed_below(slow_ma)
	pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=273)
	print(element + ": " + str(pf.total_profit()))
	total_profit += pf.total_profit()
	print(pf.stats())

print(total_profit)