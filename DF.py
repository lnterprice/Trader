import pandas as pd
import warnings
import pdb
warnings.simplefilter(action='ignore', category=FutureWarning)
# Enhanced Dataframe
class EDF:
    df = None
    def __init__(self, df):
        self.df = df
        self.df['buy'] = None
        self.df['sell'] = None

    # Tested 02-28-24
    def insertIndicators(self, col1, col2):
        i = 1
        indexes = []
        while(i < len(self.df.values) - 1):
            x1 = self.df['epoch'][i]
            y1 = self.df[col1][i]
            x2 = self.df['epoch'][i+1]
            y2 = self.df[col1][i+1]
            x3 = self.df['epoch'][i]
            y3 = self.df[col2][i]
            x4 = self.df['epoch'][i+1]
            y4 = self.df[col2][i+1]
            slopeSlow = self.__returnLine(x1, y1, x2, y2)[0]
            slopeFast = self.__returnLine(x3, y3, x4, y4)[0]
            intercepts = self.__interception(x1, y1, x2, y2, x3, y3, x4, y4)
            if intercepts:
                x = intercepts[0]
                y = intercepts[1]
                tempDict = {'epoch': x, col1: y, col2: y}
                for column in self.getColumns()[1:]:
                    if self.df[column].dtype == float and (column != 'buy' and column != 'sell'):
                        slope = self.__returnLine(x1, self.df[column][i], x2, self.df[column][i+1])
                        tempDict[column]  = (x*slope[0] + slope[1])


                if(slopeSlow == intercepts[2]):
                    tempDict['sell'] = tempDict['price']
                    self.addRow(i, tempDict)
                    indexes.append(i+1)
                    i += 1
                if(slopeFast == intercepts[2]):
                    tempDict['buy'] = tempDict['price']
                    self.addRow(i, tempDict)
                    indexes.append(i+1)
                    i += 1
            i += 1
        self.updateTime()
        return indexes

    # Tested 02-28-24
    def updateTime(self):
        time = pd.to_datetime(self.getRows('epoch'), unit='s')
        time = (time).dt.tz_localize("UTC")
        time = (time).dt.tz_convert('America/Los_Angeles')
        time = (time).dt.time
        time = [t.strftime('%I:%M:%S %p') for t in time]
        self.setColumnI('time', 1, time)
    
    # Tested 02-28-24
    def getRows(self, column):
        return self.df[column]
    
    def split(self, startRow=None, endRow=None):
        if startRow or endRow:
            if startRow and endRow:
                return EDF(self.rawDF().iloc[startRow:endRow])
            else:
                return (EDF(self.rawDF().iloc[startRow:]), EDF(self.rawDF().iloc[:startRow]))
        else:
            return None

    # Tested 02-28-24
    def getColumns(self):
        return list(self.df)
    
    # Tested 02-28-24, will append values between index and index + 1.
    def addRow(self, index, data):
        data = pd.DataFrame(data, index=[index])
        if index == -1:
            self.df = pd.concat([data, self.df.iloc[0:]]).reset_index(drop=True)
        elif index == self.size():
            self.df = pd.concat([self.df.iloc[:index], data]).reset_index(drop=True)
        else:
            self.df = pd.concat([self.df.iloc[:index+1], data, self.df.iloc[index+1:]]).reset_index(drop=True)
    
    def renameCol(self, o, n):
        self.df = self.df.rename(columns={o:n})

    # Tested 02-28-24, type(data) = dictionary
    def changeRow(self, index, data):
        self.df.iloc[index] = data
    
    def deleteCol(self, colName):
        if type(colName) == list:
            for col in colName:
                self.df.pop(col)
        elif type(colName) == str:
            self.df.pop(colName)
        else:
            return None

    # Tested 02-28-24
    def deleteRow(self, index):
        self.df = self.df.drop(index)

    # Tested 02-28-24
    # Updated 02-29-24
    # Tested 02-29-24
    def setColumn(self, name, rows=None):
        self.df[name] = rows

    # Tested 02-29-24
    def setColumnI(self, name, index, rows=None):
        if name in self.getColumns():
            self.setColumn(name, rows)
        else:
            self.df.insert(index, name, rows)
    
    def getValue(self, column, index):
        return self.df[column][index]

    # Tested 02-28-24
    def size(self):
        return len(self.df.values)

    # Tested 02-28-24
    def __returnLine(self, x1, y1, x2, y2):
        slope = (y2 - y1) / (x2 - x1)
        b = y1 - (slope * x1)
        return slope, b
    
    # Tested 02-28-24
    def __interception(self, x1, y1, x2, y2, x3, y3, x4, y4):
        slope1, b1 = self.__returnLine(x1, y1, x2, y2)
        slope2, b2 = self.__returnLine(x3, y3, x4, y4)
        value = (b2-b1) / (slope1 - slope2)
        if(value <= x2 and value >= x1):
            return value, (slope1 * value) + b1, slope1 if slope1 >= slope2 else slope2
        return False

    def show(self):
        print(self.df)

    # Tested 02-28-24
    def returnDF(self):
        return EDF(self.df)

    def rawDF(self):
        return self.df
    