import torch
import os
import pickle
from config import config
from FlexArrayObj import FlexArray
class BuyObj:
    def __init__(self, SymbolObj):
        self.symbol = SymbolObj.returnSymbol()
        self.MODELPATH = os.path.join(os.environ['MODELPATH'], self.symbol + '.pkl')
        self.Obj = SymbolObj
        with open(self.MODELPATH, 'rb') as file:
            self.model, self.min, self.max = pickle.load(file)

    def predictNext(self, batch):

        x = torch.tensor(batch).float().to(config["training"]["device"]).unsqueeze(0).unsqueeze(2)
        prediction = self.model(x)
        prediction = prediction.cpu().detach().numpy()

        prediction = FlexArray(prediction, self.min, self.max).denormalize()
        return prediction[0]
    
    
    
