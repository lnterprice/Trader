import pandas as pd
# Enhanced Dataframe
class EDF:
    df = None
    def __init__(self, df):
        self.df = df
    
    # Tested 02-28-24
    def insertIndicators(self, col1, col2):
        i = 0
        indexes = []
        self.df.assign(buy=None)
        self.df.assign(sell=None)
        while(i < len(self.df.values) - 1):
            x1 = self.df['date'][i]
            y1 = self.df[col1][i]
            x2 = self.df['date'][i+1]
            y2 = self.df[col1][i+1]
            x3 = self.df['date'][i]
            y3 = self.df[col2][i]
            x4 = self.df['date'][i+1]
            y4 = self.df[col2][i+1]
            slopeSlow = self.__returnLine(x1, y1, x2, y2)[0]
            slopeFast = self.__returnLine(x3, y3, x4, y4)[0]
            intercepts = self.__interception(x1, y1, x2, y2, x3, y3, x4, y4)
            if intercepts:
                x = intercepts[0]
                y = intercepts[1]
                if(slopeSlow == intercepts[2]):
                    self.addRow(i, {'date': x, 'sell': y})
                    indexes.append(i+1)
                if(slopeFast == intercepts[2]):
                    self.addRow(i, {'date': x, 'buy': y})
                    indexes.append(i+1)
            i += 1
        return indexes

    # Tested 02-28-24
    def to12Hours(self):
        time = pd.to_datetime(self.getRows('date'), unit='s')
        time = (time).dt.tz_localize("UTC")
        time = (time).dt.tz_convert('America/Los_Angeles')
        time = (time).dt.time
        time = [t.strftime('%I:%M:%S %p') for t in time]
        self.setColumn('date', time)

    # Tested 02-28-24
    def getRows(self, column):
        return self.df[column]
    
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
    
    # Tested 02-28-24, type(data) = dictionary
    def changeRow(self, index, data):
        self.df.iloc[index] = data
    
    # Tested 02-28-24
    def deleteRow(self, index):
        self.df = self.df.drop(index)

    # Tested 02-28-24
    def setColumn(self, name, rows=None):
        self.df[name] = rows
    
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
    
    # Tested 02-28-24
    def returnDF(self):
        return self.df

    