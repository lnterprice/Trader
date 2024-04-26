import torch.nn as nn
from config import config

class LSTMModel(nn.Module):
    def __init__(self, inputSize = config['model']['inputSize'], LSTMSize = config['model']['lstmSize'], numLayers = config['model']['numLayers'], outputSize = 1, dropOut = config['model']['dropOut']):
        super().__init__()
        self.LSTMSize = LSTMSize
        self.linear1 = nn.Linear(inputSize, LSTMSize)
        self.relu = nn.ReLU()
        self.LSTM = nn.LSTM(LSTMSize, hidden_size=self.LSTMSize, num_layers = numLayers, batch_first = True)
        self.dropout = nn.Dropout(dropOut)
        self.linear2 = nn.Linear(numLayers*LSTMSize, outputSize)
        self.init_weights()
    
    def init_weights(self):
        for name, param in self.LSTM.named_parameters():
            if 'bias' in name:
                nn.init.constant(param, 0.0)
            elif 'weight_ih' in name:
                 nn.init.kaiming_normal_(param)
            elif 'weight_hh' in name:
                 nn.init.orthogonal_(param)

    def forward(self, x):
        batchSize = x.shape[0]
        x = self.linear1(x)
        x = self.relu(x)
        LSTMOut, (hiddenState, cellState) = self.LSTM(x)
        x = hiddenState.permute(1, 0, 2).reshape(batchSize, -1)
        x = self.dropout(x)
        predictions = self.linear2(x)
        return predictions[:, -1]