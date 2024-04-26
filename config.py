config = {
    "data": {
        "windowSize": 20,
        "trainSplitSize": 0.85
    },
    "model": {
        "inputSize": 1, #price
        "numLayers": 2,
        "lstmSize": 32,
        "dropOut": 0.2
    },
    "training": {
        "device": "cuda",
        "batchSize": 64,
        "epoch": 100,
        "learningRate": 0.01,
        "stepSize": 40
    }
}