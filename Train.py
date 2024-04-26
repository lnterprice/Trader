import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import os
import pdb
import pandas as pd
import pickle
from torch.utils.data import DataLoader
from DF import EDF
from config import config
from LSTM import LSTMModel
from TimeSeries import TimeSeriesDataset
from FlexArrayObj import FlexArray
DATASHEETS = os.environ['DATA_SHEETS']

def prepX(x, windowSize):
    #pdb.set_trace()
    numRow = x.shape[0] - windowSize + 1
    shape = (numRow, windowSize)
    strides = (x.strides[0], x.strides[0])
    output = np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)
    return output

def prepY(x, windowSize):
    output = x[windowSize:]
    return output

def prepData(data, split):
    split = int(len(data) * split)
    dataX= prepX(data, windowSize=config['data']['windowSize'])
    dataY = prepY(data, windowSize=config['data']['windowSize'])
    dataXTrain = dataX[:split]
    dataXVal = dataX[split:]
    dataYTrain = dataY[:split]
    dataYVal = dataY[split:]
    return dataXTrain, dataXVal, dataYTrain, dataYVal
    

def runEpoch(dataLoader, training=False):
    epochLoss = 0
    if training:
        model.train()
    else:
        model.eval()

    for i, (x, y) in enumerate(dataLoader):
        if training:
            optimizer.zero_grad()
        
        batchSize = x.shape[0]

        x = x.to(config["training"]["device"])
        y = y.to(config["training"]["device"])
        #pdb.set_trace()
        out = model(x)
        loss = criterion(out.contiguous(), y.contiguous())

        if training:
            loss.backward()
            optimizer.step()
        
        epochLoss += (loss.detach().item() / batchSize)

    lr = scheduler.get_last_lr()[0]

    return epochLoss, lr
MODELPATH = os.environ['MODELPATH']
symbols = input("[+] Please enter the symbols you want to create models for here seperated by a single space > ")
symbols = symbols.upper()
symbols = symbols.split()
dfs = []
for symbol in symbols:
    #pdb.set_trace()
    tempDf = pd.DataFrame()
    for dir in os.listdir(DATASHEETS):
        csvPath = os.path.join(DATASHEETS, dir, symbol + '.csv')
        if os.path.exists(csvPath):
            tempDf = pd.concat([tempDf, pd.read_csv(csvPath)], ignore_index=True)
    if len(tempDf) != 0:
        dfs.append(tempDf)
    print(f'Length of {symbol} dataframe is {len(tempDf)}')

for i, df in enumerate(dfs):
    edf = EDF(df)
    arrayObj = FlexArray(edf.getRows('price').values)
    normalized = arrayObj.normalize()
    min = arrayObj.getMin()
    max = arrayObj.getMax()
    edf.setColumn('price', normalized)
    edf.deleteCol(['color', 'custom_data', 'buy', 'sell', 'date'])
    data = edf.getRows('price').values
    xTrain, xTest, yTrain, yTest = prepData(data, config['data']['trainSplitSize'])
    dsTrain = TimeSeriesDataset(xTrain, yTrain)
    dsTest = TimeSeriesDataset(xTest, yTest)
    model = LSTMModel(inputSize=config["model"]["inputSize"], LSTMSize=config["model"]["lstmSize"], numLayers=config["model"]["numLayers"], outputSize=1, dropOut=config["model"]["dropOut"])
    model = model.to(config["training"]["device"])
    trainDataLoader = DataLoader(dsTrain, batch_size=config['training']['batchSize'], shuffle=True)
    testDataLoader = DataLoader(dsTest, batch_size=config['training']['batchSize'], shuffle=True)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=config["training"]["learningRate"], betas=(0.9, 0.98), eps=1e-9)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=config["training"]["stepSize"], gamma=0.1)
    print(f'\n{symbols[i]} training...\n')
    for epoch in range(config["training"]["epoch"]):
        loss_train, lr_train = runEpoch(trainDataLoader, training=True)
        loss_val, lr_val = runEpoch(testDataLoader)
        scheduler.step()
        
        print('Epoch[{}/{}] | loss train:{:.6f}, test:{:.6f} | lr:{:.6f}'
                .format(epoch+1, config["training"]["epoch"], loss_train, loss_val, lr_train))
    picklePath = os.path.join(MODELPATH, symbols[i] + '.pkl')
    with open (picklePath, 'wb') as file:
        pickle.dump((model, min, max), file)