from config import config
from BuyObj import BuyObj
from SymbolObj import Symbol
from FlexArrayObj import FlexArray
from GetDatapoints import DataPoints
from DF import EDF
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Datapoints object which is used to concat all of the DFS
dataPointsObj = DataPoints()
# Creates a symbol object for the symbol using the dataPointsObj session; used to initialize a buy obj, which is used to predict the next price
symbolObj = Symbol(dataPointsObj.getSession(), 'NVDA')
# A concated DF is made from the dataPointsObj function with the symbol object as a parameter
concatedDF = dataPointsObj.concatDFS(symbolObj)
# Buy object is finally initialized
buyObj = BuyObj(symbolObj)
# FlexArray is initialized with normal values as a parameter
array = FlexArray(concatedDF['price'].values)
# Array is normalized for the buyObj function
normalizedArray = array.normalize()
# Next value is predicted based on the last 20 normalized values


def runSimulation(actualDF, numVals):
    actualVals = actualDF['price'].values[-numVals:]
    totalProfit = 0
    success = 0
    failure = 0
    for i in range(len(actualVals)-1):
        currentPrice = actualVals[i]
        batch = actualDF['price'].values[-numVals-20+i:-numVals+i]
        batch = FlexArray(batch, actualDF['price'].values.min(), actualDF['price'].values.max())
        batch = batch.normalize()
        predictedPrice = buyObj.predictNext(batch)
        nextPrice = actualVals[i+1]

        if predictedPrice > currentPrice:
            totalProfit -= currentPrice
            totalProfit += nextPrice
            if nextPrice - currentPrice > 0:
                success += 1
            else:
                failure += 1
        elif predictedPrice < currentPrice:
            totalProfit += currentPrice
            totalProfit -= nextPrice
            if currentPrice - nextPrice > 0:
                success += 1
            else:
                failure += 1
    
    plt.plot(actualDF['date'].values[-758:], actualDF['price'].values[-758:])
    plt.show()
    print(f'Success rate of {100*(success / (success+failure))} and a profit of {totalProfit}')

    #pdb.set_trace()

runSimulation(concatedDF, 758)