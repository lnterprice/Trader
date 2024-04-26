import numpy as np

class FlexArray:
    def __init__(self, array, min=None, max=None):
        self.numpyArray = array
        if min or max:
            if min:
                self.min = min
            if max:
                self.max = max
        else:
            self.min = np.min(array)
            self.max = np.max(array)

    def normalize(self):
        self.numpyArray = (self.numpyArray - self.min) / (self.max - self.min) 
        return self.numpyArray

    def denormalize(self):
        self.numpyArray = (self.numpyArray * (self.max - self.min)) + self.min
        return self.numpyArray
    
    def getMax(self):
        return self.max
    
    def getMin(self):
        return self.min