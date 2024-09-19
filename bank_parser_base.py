import pandas as pd
import logging

class BankParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self):
        self.df = pd.read_csv(self.filepath)
        return self.process()

    def process(self):
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement the process method")