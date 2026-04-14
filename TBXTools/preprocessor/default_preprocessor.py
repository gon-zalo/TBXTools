class DefaultPreprocessor:

    def __init__(self):
        pass

    def process(self, x):
        return x
    
    def case_normalization(self, x):
        return x.lower()